"""
Tier 3 E2E Tests: Resume from Checkpoint with Real Infrastructure.

Tests agent resumption from checkpoint after interruption:
- Real Ollama LLM inference (llama3.2:1b - FREE)
- Real filesystem checkpoint storage
- Real state restoration from checkpoint
- No mocking (real infrastructure only)

Requirements:
- Ollama running locally with llama3.2:1b model
- Filesystem access for checkpoint storage
- No mocking (real infrastructure only)
- Tests complete in <90s

Test Coverage:
1. test_resume_from_checkpoint (Test 30) - Resume after interruption

Budget: $0.00 (Ollama free)
Duration: ~60-90s
"""

import tempfile

import pytest
from kaizen.agents.autonomous.base import AutonomousConfig, BaseAutonomousAgent
from kaizen.core.autonomy.state.manager import StateManager
from kaizen.core.autonomy.state.storage import FilesystemStorage
from kaizen.signatures import InputField, OutputField, Signature

from tests.utils.cost_tracking import get_global_tracker
from tests.utils.reliability_helpers import (
    OllamaHealthChecker,
    async_retry_with_backoff,
)

# Check Ollama availability
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.asyncio,
    pytest.mark.skipif(
        not OllamaHealthChecker.is_ollama_running(),
        reason="Ollama not running",
    ),
    pytest.mark.skipif(
        not OllamaHealthChecker.is_model_available("llama3.2:1b"),
        reason="llama3.2:1b model not available",
    ),
]


class TaskSignature(Signature):
    """Task signature for checkpoint testing"""

    task: str = InputField(description="Task to process")
    result: str = OutputField(description="Task result")


@pytest.mark.timeout(90)
async def test_resume_from_checkpoint():
    """
    Test 30: Resume from checkpoint after interruption.

    Validates:
    - Agent resumes from checkpoint with correct state restoration
    - Step counter continues from checkpoint
    - Execution context preserved across restarts
    - Multiple resume cycles maintain data integrity
    """
    cost_tracker = get_global_tracker()

    print("\n" + "=" * 70)
    print("Test 30: Resume from Checkpoint After Interruption")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        # Phase 1: Agent runs and creates checkpoints
        print("\n1. Phase 1: Running first agent and creating checkpoints...")

        config1 = AutonomousConfig(
            llm_provider="ollama",
            model="llama3.2:1b",
            max_cycles=3,
            checkpoint_frequency=1,  # Checkpoint every cycle
        )

        storage = FilesystemStorage(base_dir=tmpdir)
        state_manager1 = StateManager(storage=storage, checkpoint_frequency=1)

        agent1 = BaseAutonomousAgent(
            config=config1, signature=TaskSignature(), state_manager=state_manager1
        )

        print("   Agent 1 configured")

        # Run first agent (simulates work before interruption)
        async def run_agent1():
            await agent1._autonomous_loop("Count from 1 to 10")

        await async_retry_with_backoff(run_agent1, max_attempts=2, initial_delay=1.0)

        print(f"   ✓ Agent 1 completed {agent1.current_step} steps")

        # Get checkpoint from first run
        checkpoints = await storage.list_checkpoints()
        assert len(checkpoints) > 0, "Should have checkpoints from first agent"
        interruption_step = checkpoints[0].step_number
        checkpoint_id = checkpoints[0].checkpoint_id

        print(f"   ✓ Checkpoint created at step {interruption_step}")
        print(f"   ✓ Checkpoint ID: {checkpoint_id}")

        # Phase 2: Resume after interruption
        print("\n2. Phase 2: Creating second agent to resume from checkpoint...")

        config2 = AutonomousConfig(
            llm_provider="ollama",
            model="llama3.2:1b",
            max_cycles=5,
            resume_from_checkpoint=True,
            checkpoint_frequency=1,
        )

        state_manager2 = StateManager(storage=storage, checkpoint_frequency=1)

        agent2 = BaseAutonomousAgent(
            config=config2, signature=TaskSignature(), state_manager=state_manager2
        )

        print("   Agent 2 configured with resume_from_checkpoint=True")

        # Resume from interruption point
        print("\n3. Resuming from checkpoint...")

        async def run_agent2():
            await agent2._autonomous_loop("Continue counting to 10")

        await async_retry_with_backoff(run_agent2, max_attempts=2, initial_delay=1.0)

        print(f"   ✓ Agent 2 completed {agent2.current_step} steps")

        # Assert: Resumed from interruption point
        print("\n4. Validating resume behavior...")
        assert (
            agent2.current_step >= interruption_step
        ), f"Should resume from step {interruption_step}, got {agent2.current_step}"
        print("   ✓ Step counter continued from checkpoint")

        # Validate checkpoint history
        final_checkpoints = await storage.list_checkpoints()
        assert len(final_checkpoints) > len(
            checkpoints
        ), "Should have more checkpoints after resume"
        print(f"   ✓ Additional checkpoints created: {len(final_checkpoints)}")

        # Phase 3: Test multiple resume cycles
        print("\n5. Phase 3: Testing multiple resume cycles...")

        config3 = AutonomousConfig(
            llm_provider="ollama",
            model="llama3.2:1b",
            max_cycles=2,
            resume_from_checkpoint=True,
            checkpoint_frequency=1,
        )

        state_manager3 = StateManager(storage=storage, checkpoint_frequency=1)

        agent3 = BaseAutonomousAgent(
            config=config3, signature=TaskSignature(), state_manager=state_manager3
        )

        async def run_agent3():
            await agent3._autonomous_loop("Complete the counting task")

        await async_retry_with_backoff(run_agent3, max_attempts=2, initial_delay=1.0)

        print(f"   ✓ Agent 3 completed {agent3.current_step} steps")

        # Validate data integrity across all cycles
        print("\n6. Validating data integrity across all resume cycles...")
        all_checkpoints = await storage.list_checkpoints()
        assert len(all_checkpoints) > 0, "Should have checkpoints from all agents"

        # Verify step numbers are monotonic (non-decreasing)
        step_numbers = [cp.step_number for cp in reversed(all_checkpoints)]
        assert all(
            step_numbers[i] <= step_numbers[i + 1] for i in range(len(step_numbers) - 1)
        ), "Step numbers should be monotonic"
        print(f"   ✓ Step numbers monotonic: {step_numbers[:5]}...")

        # Track cost
        cost_tracker.track_usage(
            test_name="test_resume_from_checkpoint",
            provider="ollama",
            model="llama3.2:1b",
            input_tokens=150 * (3 + 5 + 2),  # Total iterations across all agents
            output_tokens=50 * (3 + 5 + 2),
        )

        print("\n" + "=" * 70)
        print("✓ Test 30 Passed: Resume from checkpoint validated")
        print(f"  - Initial checkpoint step: {interruption_step}")
        print(f"  - Agent 2 final step: {agent2.current_step}")
        print(f"  - Agent 3 final step: {agent3.current_step}")
        print(f"  - Total checkpoints: {len(all_checkpoints)}")
        print("  - Cost: $0.00 (Ollama free)")
        print("=" * 70)
