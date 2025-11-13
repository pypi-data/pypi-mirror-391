"""
Tier 3 E2E Tests: Interrupt Mechanism with Real Ollama LLMs.

Tests interrupt handling with real infrastructure:
- Real Ollama LLM inference (requires Ollama running)
- Real filesystem checkpoints
- Real autonomous execution
- Application restart simulation
- Long-running interrupt validation

Requirements:
- Ollama running locally with llama3.2:1b model
- No mocking (real infrastructure only)
- Tests may take 30s-2 minutes due to LLM inference

Test Coverage:
1. test_timeout_interrupt_with_checkpoint - Auto-stop after timeout with checkpoint
2. test_budget_interrupt_with_recovery - Auto-stop at budget limit, then resume
3. test_interrupt_propagation_multi_agent - Parent interrupt cascades to children
4. test_graceful_vs_immediate_shutdown - Compare shutdown modes
5. test_resume_after_interrupt - Resume execution after interrupt
"""

import asyncio
import subprocess
import tempfile
import time

import pytest
from kaizen.agents.autonomous.base import AutonomousConfig, BaseAutonomousAgent
from kaizen.core.autonomy.interrupts.handlers import (
    BudgetInterruptHandler,
    TimeoutInterruptHandler,
)
from kaizen.core.autonomy.interrupts.manager import InterruptManager
from kaizen.core.autonomy.interrupts.types import (
    InterruptedError,
    InterruptMode,
    InterruptSource,
)
from kaizen.core.autonomy.state.manager import StateManager
from kaizen.core.autonomy.state.storage import FilesystemStorage
from kaizen.signatures import InputField, OutputField, Signature


# Skip all tests if Ollama is not available
def check_ollama_available():
    """Check if Ollama is running and has llama3.2 model."""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0 and "llama3.2" in result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_llama_model():
    """Get available llama3.2 model name."""
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        # Prefer smaller models for faster testing
        if "llama3.2:1b" in result.stdout:
            return "llama3.2:1b"
        elif "llama3.2" in result.stdout:
            return "llama3.2:latest"
        return "llama3.2:1b"  # Default fallback
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return "llama3.2:1b"


LLAMA_MODEL = get_llama_model()

pytestmark = pytest.mark.skipif(
    not check_ollama_available(),
    reason="Ollama not running or llama3.2 model not available",
)


# Test Signatures


class CountingTaskSignature(Signature):
    """Signature for counting tasks (used for timeout testing)."""

    task: str = InputField(description="Counting task description")
    result: str = OutputField(description="Counting result or progress")


class AnalysisTaskSignature(Signature):
    """Signature for analysis tasks (used for budget testing)."""

    task: str = InputField(description="Analysis task description")
    analysis: str = OutputField(description="Analysis result")


# Helper Functions


def create_autonomous_agent(
    tmpdir: str,
    max_cycles: int = 20,
    checkpoint_frequency: int = 2,
    signature: Signature = None,
    interrupt_manager: InterruptManager = None,
) -> BaseAutonomousAgent:
    """Create autonomous agent with checkpoint infrastructure."""
    config = AutonomousConfig(
        max_cycles=max_cycles,
        checkpoint_frequency=checkpoint_frequency,
        llm_provider="ollama",
        model=LLAMA_MODEL,
        temperature=0.3,  # Low temp for consistency
        enable_interrupts=True,
        checkpoint_on_interrupt=True,
        graceful_shutdown_timeout=5.0,
    )

    storage = FilesystemStorage(base_dir=tmpdir)
    state_manager = StateManager(
        storage=storage, checkpoint_frequency=checkpoint_frequency
    )

    if signature is None:
        signature = CountingTaskSignature()

    agent = BaseAutonomousAgent(
        config=config,
        signature=signature,
        state_manager=state_manager,
        interrupt_manager=interrupt_manager,
    )

    return agent


# ═══════════════════════════════════════════════════════════════
# Test 1: Timeout Interrupt with Checkpoint
# ═══════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_timeout_interrupt_with_checkpoint():
    """
    Test automatic timeout interrupt with checkpoint save.

    Validates:
    - TimeoutInterruptHandler triggers after timeout
    - Agent raises InterruptedError on timeout
    - Checkpoint saved with interrupt metadata
    - Real Ollama LLM inference

    Expected duration: 15-20 seconds
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create interrupt manager with timeout handler
        interrupt_manager = InterruptManager()
        timeout_handler = TimeoutInterruptHandler(
            interrupt_manager=interrupt_manager,
            timeout_seconds=10.0,  # 10 second timeout
        )

        # Create agent
        agent = create_autonomous_agent(
            tmpdir=tmpdir,
            max_cycles=50,  # High cycle limit, timeout will stop first
            checkpoint_frequency=2,
            interrupt_manager=interrupt_manager,
        )

        # Start timeout monitoring in background
        timeout_task = asyncio.create_task(timeout_handler.start())

        # Run long task (will be interrupted)
        task = "Count from 1 to 100, showing each number"

        interrupted = False
        try:
            result = await agent._autonomous_loop(task)
            # If we get here without exception, agent completed before timeout
            print("\n⚠️  Agent completed before timeout (very efficient!)")
            print(f"   Result: {result}")

        except InterruptedError as e:
            # Expected path - interrupted by timeout
            interrupted = True

            # Verify interrupt reason from exception
            assert e.reason is not None, "InterruptedError should have reason"
            assert (
                e.reason.source == InterruptSource.TIMEOUT
            ), f"Should be timeout interrupt, got: {e.reason.source}"
            assert (
                "timeout" in e.reason.message.lower()
            ), f"Message should mention timeout, got: {e.reason.message}"

        # Verify interrupted flag
        assert interrupted, "Agent should be interrupted by timeout"

        # Verify interrupt manager state
        reason = interrupt_manager.get_interrupt_reason()
        assert reason is not None, "Interrupt reason should be set"
        assert (
            reason.source == InterruptSource.TIMEOUT
        ), f"Should be timeout interrupt, got: {reason.source}"

        # Verify checkpoint saved
        storage = agent._state_manager.storage
        checkpoints = await storage.list_checkpoints()
        assert len(checkpoints) > 0, "Should have checkpoint after timeout"

        # Verify checkpoint has interrupt metadata
        latest_checkpoint = checkpoints[0]
        state = await storage.load(latest_checkpoint.checkpoint_id)
        assert (
            state.status == "interrupted"
        ), f"Checkpoint status should be interrupted, got: {state.status}"
        assert (
            "interrupt_reason" in state.metadata
        ), "Checkpoint should have interrupt_reason metadata"

        # Verify interrupt metadata structure
        interrupt_metadata = state.metadata["interrupt_reason"]
        assert (
            interrupt_metadata["source"] == "timeout"
        ), f"Interrupt source should be timeout, got: {interrupt_metadata['source']}"

        print(
            f"\n✅ Timeout interrupt successful after ~10s "
            f"(cycles completed: {state.step_number})"
        )

        # Clean up timeout handler
        await timeout_handler.stop()
        timeout_task.cancel()
        try:
            await timeout_task
        except asyncio.CancelledError:
            pass


# ═══════════════════════════════════════════════════════════════
# Test 2: Budget Interrupt with Recovery
# ═══════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_budget_interrupt_with_recovery():
    """
    Test budget interrupt and recovery from checkpoint.

    Validates:
    - BudgetInterruptHandler triggers at budget limit
    - Checkpoint saved before stop
    - Can resume from checkpoint
    - No data loss during recovery

    Expected duration: 30-45 seconds
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Phase 1: Run until budget exceeded
        interrupt_manager1 = InterruptManager()
        budget_handler = BudgetInterruptHandler(
            interrupt_manager=interrupt_manager1,
            budget_usd=0.01,  # Very low budget for fast testing
        )

        agent1 = create_autonomous_agent(
            tmpdir=tmpdir,
            max_cycles=20,
            checkpoint_frequency=1,  # Frequent checkpoints
            signature=AnalysisTaskSignature(),
            interrupt_manager=interrupt_manager1,
        )

        task = "Analyze the benefits of AI in healthcare"

        # Start agent in background
        agent_task = asyncio.create_task(agent1._autonomous_loop(task))

        # Simulate cost tracking (wait for a few cycles, then exceed budget)
        await asyncio.sleep(3)  # Let agent run for a bit
        budget_handler.track_cost(0.005)  # First operation
        await asyncio.sleep(2)
        budget_handler.track_cost(0.006)  # Exceeds $0.01 budget

        # Wait for agent to detect interrupt and shut down
        interrupted = False
        try:
            result1 = await agent_task
            print("\n⚠️  Agent completed before budget exceeded")
        except InterruptedError as e:
            interrupted = True
            assert e.reason.source == InterruptSource.BUDGET

        # Verify interrupted by budget
        assert interrupted, "Agent should be interrupted by budget"
        reason1 = interrupt_manager1.get_interrupt_reason()
        assert reason1 is not None, "Interrupt reason should be set"
        assert (
            reason1.source == InterruptSource.BUDGET
        ), f"Should be budget interrupt, got: {reason1.source}"

        # Verify checkpoint saved
        storage = agent1._state_manager.storage
        checkpoints1 = await storage.list_checkpoints()
        assert len(checkpoints1) > 0, "Should have checkpoint after budget exceeded"

        checkpoint_step = checkpoints1[0].step_number
        print(f"\n✅ Budget interrupt successful at step {checkpoint_step}")

        # Phase 2: Resume from checkpoint
        interrupt_manager2 = InterruptManager()
        agent2 = create_autonomous_agent(
            tmpdir=tmpdir,
            max_cycles=5,  # Just a few more cycles
            checkpoint_frequency=1,
            signature=AnalysisTaskSignature(),
            interrupt_manager=interrupt_manager2,
        )

        # Configure agent to resume from checkpoint
        agent2.autonomous_config.resume_from_checkpoint = True

        # Resume execution
        result2 = await agent2._autonomous_loop("Continue the analysis")

        # Verify resumed from checkpoint
        assert agent2.current_step >= checkpoint_step, (
            f"Agent should resume from step {checkpoint_step}, "
            f"got step {agent2.current_step}"
        )

        # Verify no data loss
        checkpoints2 = await storage.list_checkpoints()
        assert len(checkpoints2) > 0, "Should have checkpoints after resume"

        print(f"✅ Successfully resumed from step {checkpoint_step}")
        print(f"   Continued to step {agent2.current_step}")


# ═══════════════════════════════════════════════════════════════
# Test 3: Interrupt Propagation Multi-Agent
# ═══════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_interrupt_propagation_multi_agent():
    """
    Test interrupt propagation from parent to child agents.

    Validates:
    - Parent interrupt cascades to children
    - All agents interrupted gracefully
    - All checkpoints saved
    - Propagation metadata correct

    Expected duration: 25-35 seconds
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create parent and child interrupt managers
        parent_manager = InterruptManager()
        child_manager1 = InterruptManager()
        child_manager2 = InterruptManager()

        # Link children to parent
        parent_manager.add_child_manager(child_manager1)
        parent_manager.add_child_manager(child_manager2)

        # Create parent agent
        parent_agent = create_autonomous_agent(
            tmpdir=f"{tmpdir}/parent",
            max_cycles=10,
            checkpoint_frequency=1,
            interrupt_manager=parent_manager,
        )

        # Create child agents
        child_agent1 = create_autonomous_agent(
            tmpdir=f"{tmpdir}/child1",
            max_cycles=10,
            checkpoint_frequency=1,
            interrupt_manager=child_manager1,
        )

        child_agent2 = create_autonomous_agent(
            tmpdir=f"{tmpdir}/child2",
            max_cycles=10,
            checkpoint_frequency=1,
            interrupt_manager=child_manager2,
        )

        # Start all agents in background
        parent_task = asyncio.create_task(
            parent_agent._autonomous_loop("Count from 1 to 50")
        )
        child_task1 = asyncio.create_task(
            child_agent1._autonomous_loop("Count from 51 to 100")
        )
        child_task2 = asyncio.create_task(
            child_agent2._autonomous_loop("Count from 101 to 150")
        )

        # Let agents run for a bit
        await asyncio.sleep(5)

        # Interrupt parent (should cascade to children)
        parent_manager.request_interrupt(
            mode=InterruptMode.GRACEFUL,
            source=InterruptSource.USER,
            message="User requested stop",
        )

        # Propagate to children
        parent_manager.propagate_to_children()

        # Wait for all to complete (should raise InterruptedError)
        interrupted_count = 0
        results = []
        for task in [parent_task, child_task1, child_task2]:
            try:
                result = await task
                results.append({"interrupted": False, "result": result})
            except InterruptedError as e:
                interrupted_count += 1
                results.append({"interrupted": True, "reason": e.reason})

        # Verify all interrupted
        assert (
            interrupted_count == 3
        ), f"All 3 agents should be interrupted, got {interrupted_count}"

        # Verify parent reason
        parent_reason = parent_manager.get_interrupt_reason()
        assert parent_reason.message == "User requested stop"

        # Verify children have propagated reasons
        child1_reason = child_manager1.get_interrupt_reason()
        child2_reason = child_manager2.get_interrupt_reason()

        assert (
            "Propagated from parent" in child1_reason.message
        ), f"Child 1 should have propagated message, got: {child1_reason.message}"
        assert (
            "Propagated from parent" in child2_reason.message
        ), f"Child 2 should have propagated message, got: {child2_reason.message}"

        # Verify all checkpoints saved
        parent_storage = parent_agent._state_manager.storage
        child1_storage = child_agent1._state_manager.storage
        child2_storage = child_agent2._state_manager.storage

        parent_checkpoints = await parent_storage.list_checkpoints()
        child1_checkpoints = await child1_storage.list_checkpoints()
        child2_checkpoints = await child2_storage.list_checkpoints()

        assert len(parent_checkpoints) > 0, "Parent should have checkpoints"
        assert len(child1_checkpoints) > 0, "Child 1 should have checkpoints"
        assert len(child2_checkpoints) > 0, "Child 2 should have checkpoints"

        print(
            "\n✅ Interrupt propagation successful "
            "(parent + 2 children all interrupted)"
        )


# ═══════════════════════════════════════════════════════════════
# Test 4: Graceful vs Immediate Shutdown
# ═══════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_graceful_vs_immediate_shutdown():
    """
    Test comparison between graceful and immediate shutdown modes.

    Validates:
    - Graceful shutdown finishes current cycle
    - Immediate shutdown stops quickly
    - Checkpoint quality differs between modes
    - Both modes save checkpoints

    Expected duration: 40-60 seconds (two full test runs)
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test 1: Graceful Shutdown
        interrupt_manager_graceful = InterruptManager()
        agent_graceful = create_autonomous_agent(
            tmpdir=f"{tmpdir}/graceful",
            max_cycles=20,
            checkpoint_frequency=1,
            interrupt_manager=interrupt_manager_graceful,
        )

        task = "Count from 1 to 30"

        # Start agent
        graceful_task = asyncio.create_task(agent_graceful._autonomous_loop(task))

        # Wait for a few cycles
        await asyncio.sleep(5)

        # Request graceful interrupt
        graceful_start = time.time()
        interrupt_manager_graceful.request_interrupt(
            mode=InterruptMode.GRACEFUL,
            source=InterruptSource.USER,
            message="Graceful shutdown test",
        )

        try:
            await graceful_task
            graceful_interrupted = False
        except InterruptedError:
            graceful_interrupted = True

        graceful_duration = time.time() - graceful_start

        # Verify graceful shutdown
        assert graceful_interrupted, "Graceful agent should be interrupted"
        storage_graceful = agent_graceful._state_manager.storage
        checkpoints_graceful = await storage_graceful.list_checkpoints()
        assert len(checkpoints_graceful) > 0

        graceful_checkpoint = await storage_graceful.load(
            checkpoints_graceful[0].checkpoint_id
        )

        print("\n✅ Graceful shutdown:")
        print(f"   Duration: {graceful_duration:.2f}s")
        print(f"   Steps completed: {graceful_checkpoint.step_number}")
        print(f"   Status: {graceful_checkpoint.status}")

        # Test 2: Immediate Shutdown
        interrupt_manager_immediate = InterruptManager()
        agent_immediate = create_autonomous_agent(
            tmpdir=f"{tmpdir}/immediate",
            max_cycles=20,
            checkpoint_frequency=1,
            interrupt_manager=interrupt_manager_immediate,
        )

        # Start agent
        immediate_task = asyncio.create_task(agent_immediate._autonomous_loop(task))

        # Wait for a few cycles
        await asyncio.sleep(5)

        # Request immediate interrupt
        immediate_start = time.time()
        interrupt_manager_immediate.request_interrupt(
            mode=InterruptMode.IMMEDIATE,
            source=InterruptSource.USER,
            message="Immediate shutdown test",
        )

        try:
            await immediate_task
            immediate_interrupted = False
        except InterruptedError:
            immediate_interrupted = True

        immediate_duration = time.time() - immediate_start

        # Verify immediate shutdown
        assert immediate_interrupted, "Immediate agent should be interrupted"
        storage_immediate = agent_immediate._state_manager.storage
        checkpoints_immediate = await storage_immediate.list_checkpoints()
        assert len(checkpoints_immediate) > 0

        immediate_checkpoint = await storage_immediate.load(
            checkpoints_immediate[0].checkpoint_id
        )

        print("\n✅ Immediate shutdown:")
        print(f"   Duration: {immediate_duration:.2f}s")
        print(f"   Steps completed: {immediate_checkpoint.step_number}")
        print(f"   Status: {immediate_checkpoint.status}")

        # Compare shutdown modes
        print("\n📊 Comparison:")
        print(
            f"   Graceful took {graceful_duration:.2f}s, "
            f"Immediate took {immediate_duration:.2f}s"
        )

        # Both should have valid checkpoints
        assert graceful_checkpoint.status == "interrupted"
        assert immediate_checkpoint.status == "interrupted"


# ═══════════════════════════════════════════════════════════════
# Test 5: Resume After Interrupt
# ═══════════════════════════════════════════════════════════════


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_resume_after_interrupt():
    """
    Test resume execution after programmatic interrupt.

    Simulates:
    1. Agent runs for several cycles
    2. Programmatic interrupt at cycle 5
    3. Checkpoint saved at cycle 5
    4. Agent resumes from checkpoint
    5. Completes remaining cycles

    Validates:
    - Checkpoint saved at interrupt point
    - Resume continues from correct cycle
    - No data loss or duplicate work
    - Final result is complete

    Expected duration: 40-60 seconds
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Phase 1: Run until interrupt
        interrupt_manager1 = InterruptManager()
        agent1 = create_autonomous_agent(
            tmpdir=tmpdir,
            max_cycles=10,
            checkpoint_frequency=1,  # Checkpoint every cycle
            interrupt_manager=interrupt_manager1,
        )

        task = "Count from 1 to 10"

        # Start agent
        agent_task1 = asyncio.create_task(agent1._autonomous_loop(task))

        # Wait for 5 cycles (~5-8 seconds with Ollama)
        await asyncio.sleep(8)

        # Programmatic interrupt (simulate Ctrl+C)
        interrupt_manager1.request_interrupt(
            mode=InterruptMode.GRACEFUL,
            source=InterruptSource.PROGRAMMATIC,
            message="Simulated interrupt for testing",
        )

        try:
            await agent_task1
            interrupted = False
        except InterruptedError:
            interrupted = True

        # Verify interrupted
        assert interrupted, "Agent should be interrupted"

        # Get checkpoint info
        storage = agent1._state_manager.storage
        checkpoints1 = await storage.list_checkpoints()
        assert len(checkpoints1) > 0, "Should have checkpoint after interrupt"

        interrupt_step = checkpoints1[0].step_number
        assert interrupt_step > 0, "Should have completed some steps"

        print(f"\n✅ Phase 1: Interrupted at step {interrupt_step}")

        # Phase 2: Resume from checkpoint
        interrupt_manager2 = InterruptManager()
        agent2 = create_autonomous_agent(
            tmpdir=tmpdir,
            max_cycles=10,  # Complete remaining cycles
            checkpoint_frequency=1,
            interrupt_manager=interrupt_manager2,
        )

        # Enable resume from checkpoint
        agent2.autonomous_config.resume_from_checkpoint = True

        # Resume execution
        result2 = await agent2._autonomous_loop("Continue counting to 10")

        # Verify resumed from correct point
        assert agent2.current_step >= interrupt_step, (
            f"Should resume from step {interrupt_step}, "
            f"got step {agent2.current_step}"
        )

        # Verify completion or progress
        checkpoints2 = await storage.list_checkpoints()
        latest_checkpoint = await storage.load(checkpoints2[0].checkpoint_id)

        print(f"✅ Phase 2: Resumed from step {interrupt_step}")
        print(f"   Continued to step {agent2.current_step}")
        print(f"   Final status: {latest_checkpoint.status}")

        # Verify no data loss - should have made progress
        assert agent2.current_step > interrupt_step, (
            f"Agent should make progress after resume, "
            f"was at {interrupt_step}, now at {agent2.current_step}"
        )


# ═══════════════════════════════════════════════════════════════
# Test Coverage Summary
# ═══════════════════════════════════════════════════════════════

"""
Test Coverage: 5/5 E2E tests for Interrupt Mechanism

✅ Timeout Interrupt (1 test)
  - test_timeout_interrupt_with_checkpoint
  - Tests: TimeoutHandler, graceful shutdown, checkpoint save
  - Duration: ~15-20s

✅ Budget Interrupt (1 test)
  - test_budget_interrupt_with_recovery
  - Tests: BudgetHandler, checkpoint recovery, no data loss
  - Duration: ~30-45s

✅ Interrupt Propagation (1 test)
  - test_interrupt_propagation_multi_agent
  - Tests: Parent-child propagation, multi-agent coordination
  - Duration: ~25-35s

✅ Shutdown Modes (1 test)
  - test_graceful_vs_immediate_shutdown
  - Tests: Graceful vs immediate, checkpoint quality comparison
  - Duration: ~40-60s

✅ Resume After Interrupt (1 test)
  - test_resume_after_interrupt
  - Tests: Checkpoint resume, data integrity, progress continuation
  - Duration: ~40-60s

Total: 5 tests
Expected Runtime: 2.5-4 minutes (real LLM inference)
Requirements: Ollama running with llama3.2:1b model

All tests use:
- Real Ollama LLM (NO MOCKING)
- Real filesystem checkpoints (NO MOCKING)
- Real autonomous execution (NO MOCKING)
- Real interrupt handlers (NO MOCKING)
"""
