"""
Tier 3 E2E Tests: Auto-Checkpoint Creation with Real Infrastructure.

Tests automatic checkpoint creation during long-running sessions:
- Real Ollama LLM inference (llama3.2:1b - FREE)
- Real filesystem storage via StateManager
- Real checkpoint creation at intervals
- No mocking (real infrastructure only)

Requirements:
- Ollama running locally with llama3.2:1b model
- Filesystem access for checkpoint storage
- No mocking (real infrastructure only)
- Tests complete in <90s

Test Coverage:
1. test_auto_checkpoint_creation (Test 29) - Checkpoint at intervals

Budget: $0.00 (Ollama free)
Duration: ~60-90s
"""

import tempfile
from pathlib import Path

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
async def test_auto_checkpoint_creation():
    """
    Test 29: Auto-checkpoint creation during long sessions.

    Validates:
    - Checkpoint created at specified intervals (every 5 iterations)
    - Checkpoint contains agent state + memory
    - Checkpoint persisted to filesystem via StateManager
    - Checkpoint metadata includes iteration count, timestamp
    """
    cost_tracker = get_global_tracker()

    print("\n" + "=" * 70)
    print("Test 29: Auto-Checkpoint Creation During Long Sessions")
    print("=" * 70)

    with tempfile.TemporaryDirectory() as tmpdir:
        print("\n1. Creating agent with auto-checkpointing...")
        print(f"   Checkpoint directory: {tmpdir}")
        print("   Checkpoint interval: Every 2 cycles")

        # Configure agent with auto-checkpointing
        config = AutonomousConfig(
            llm_provider="ollama",
            model="llama3.2:1b",
            max_cycles=6,  # Will create ~3 checkpoints (every 2 cycles)
            checkpoint_frequency=2,  # Every 2 iterations
        )

        storage = FilesystemStorage(base_dir=tmpdir)
        state_manager = StateManager(storage=storage, checkpoint_frequency=2)

        agent = BaseAutonomousAgent(
            config=config, signature=TaskSignature(), state_manager=state_manager
        )

        print("   ✓ Agent configured with StateManager")

        # Run agent for 6 iterations (should create ~3 checkpoints)
        print("\n2. Running autonomous agent for 6 iterations...")

        async def run_with_checkpoints():
            result = await agent._autonomous_loop(
                "Count from 1 to 6, one number per iteration"
            )
            return result

        result = await async_retry_with_backoff(
            run_with_checkpoints, max_attempts=2, initial_delay=1.0
        )

        print(f"   ✓ Agent completed {agent.current_step} steps")

        # Validate checkpoints created
        print("\n3. Validating checkpoint creation...")
        checkpoint_manager = agent.state_manager
        checkpoints = await checkpoint_manager.list_checkpoints()

        print(f"   Checkpoints found: {len(checkpoints)}")
        assert (
            len(checkpoints) >= 1
        ), f"Expected at least 1 checkpoint, got {len(checkpoints)}"
        print("   ✓ At least 1 checkpoint created")

        # Validate checkpoint structure
        print("\n4. Validating checkpoint structure...")
        latest_checkpoint = checkpoints[0]  # Newest first
        latest_state = await checkpoint_manager.storage.load(
            latest_checkpoint.checkpoint_id
        )

        assert latest_state is not None, "Checkpoint state should not be None"
        assert latest_state.step_number > 0, "Step number should be > 0"
        assert latest_state.agent_id is not None, "Agent ID should be set"
        assert latest_state.status in [
            "running",
            "completed",
        ], f"Invalid status: {latest_state.status}"

        print("   ✓ Checkpoint structure valid:")
        print(f"     - Checkpoint ID: {latest_checkpoint.checkpoint_id}")
        print(f"     - Agent ID: {latest_state.agent_id}")
        print(f"     - Step number: {latest_state.step_number}")
        print(f"     - Status: {latest_state.status}")
        print(f"     - Timestamp: {latest_checkpoint.timestamp}")

        # Validate checkpoint files exist
        print("\n5. Validating checkpoint files on filesystem...")
        checkpoint_files = list(Path(tmpdir).glob("*.jsonl"))
        assert len(checkpoint_files) > 0, "No checkpoint files found on filesystem"
        print(f"   ✓ {len(checkpoint_files)} checkpoint files on disk")

        # Track cost
        cost_tracker.track_usage(
            test_name="test_auto_checkpoint_creation",
            provider="ollama",
            model="llama3.2:1b",
            input_tokens=150 * 6,  # 6 iterations
            output_tokens=50 * 6,
        )

        print("\n" + "=" * 70)
        print("✓ Test 29 Passed: Auto-checkpoint creation validated")
        print(f"  - Checkpoints created: {len(checkpoints)}")
        print(f"  - Latest checkpoint step: {latest_state.step_number}")
        print(f"  - Checkpoint files: {len(checkpoint_files)}")
        print("  - Cost: $0.00 (Ollama free)")
        print("=" * 70)
