"""
Example: Handle Ctrl+C gracefully during autonomous agent execution.

This example demonstrates:
1. Signal handler registration for SIGINT (Ctrl+C)
2. Graceful shutdown with checkpoint saving
3. Resume capability after interrupt

Requirements:
- Ollama with llama3.2 model installed

Usage:
    python 01_ctrl_c_interrupt.py

    Press Ctrl+C during execution to trigger graceful shutdown.
    Run again to resume from checkpoint.
"""

import asyncio
import signal
import sys
from pathlib import Path

from kaizen.agents.autonomous.base import AutonomousConfig, BaseAutonomousAgent
from kaizen.core.autonomy.interrupts.manager import (
    InterruptManager,
    InterruptMode,
    InterruptReason,
    InterruptSource,
)
from kaizen.core.autonomy.state.manager import StateManager
from kaizen.core.autonomy.state.storage import FilesystemStorage
from kaizen.signatures import InputField, OutputField, Signature


class TaskSignature(Signature):
    """Task signature for autonomous agent."""

    task: str = InputField(description="Task to perform")
    result: str = OutputField(description="Result of task")


def setup_signal_handlers(interrupt_manager: InterruptManager):
    """Setup signal handlers for graceful shutdown."""

    def sigint_handler(signum, frame):
        """Handle SIGINT (Ctrl+C)."""
        print("\n\n⚠️  Ctrl+C detected! Initiating graceful shutdown...")
        print("   Finishing current cycle and saving checkpoint...")
        print("   Press Ctrl+C again for immediate shutdown.\n")

        if interrupt_manager.is_interrupted():
            # Second Ctrl+C - immediate shutdown
            print("⚠️  Second Ctrl+C! Immediate shutdown...\n")
            interrupt_manager.request_interrupt(
                InterruptReason(
                    source=InterruptSource.USER,
                    mode=InterruptMode.IMMEDIATE,
                    message="User requested immediate shutdown (double Ctrl+C)",
                )
            )
        else:
            # First Ctrl+C - graceful shutdown
            interrupt_manager.request_interrupt(
                InterruptReason(
                    source=InterruptSource.USER,
                    mode=InterruptMode.GRACEFUL,
                    message="User requested graceful shutdown (Ctrl+C)",
                )
            )

    signal.signal(signal.SIGINT, sigint_handler)


async def main():
    """Main execution function."""

    # Setup checkpoint directory
    checkpoint_dir = Path(".kaizen/checkpoints/ctrl_c_example")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Create interrupt manager
    interrupt_manager = InterruptManager()

    # Setup signal handlers
    setup_signal_handlers(interrupt_manager)

    # Create autonomous agent
    config = AutonomousConfig(
        llm_provider="ollama",
        model="llama3.2",
        temperature=0.7,
        max_cycles=10,
        checkpoint_frequency=1,  # Checkpoint every cycle
        resume_from_checkpoint=True,
    )

    storage = FilesystemStorage(base_dir=str(checkpoint_dir))
    state_manager = StateManager(storage=storage)

    agent = BaseAutonomousAgent(
        config=config,
        signature=TaskSignature(),
        state_manager=state_manager,
    )

    # Inject interrupt manager
    agent._interrupt_manager = interrupt_manager

    # Check for existing checkpoint
    checkpoints = list(checkpoint_dir.glob("*.jsonl"))
    if checkpoints:
        print("📂 Found existing checkpoint! Resuming from previous run...\n")
    else:
        print("🚀 Starting new autonomous execution...\n")

    print("ℹ️  Press Ctrl+C at any time to trigger graceful shutdown.")
    print("ℹ️  Press Ctrl+C twice for immediate shutdown.\n")

    # Run autonomous loop
    task = "Count from 1 to 50, showing your progress every 5 numbers"

    try:
        result = await agent._autonomous_loop(task)

        if result["status"] == "interrupted":
            print("\n✅ Gracefully interrupted and checkpoint saved!")
            print("   Run again to resume from where you left off.\n")

            # Show interrupt details
            reason = interrupt_manager.get_interrupt_reason()
            if reason:
                print(f"   Source: {reason.source.value}")
                print(f"   Mode: {reason.mode.value}")
                print(f"   Message: {reason.message}")
                print(f"   Timestamp: {reason.timestamp}\n")

            # Show checkpoint info
            checkpoints = list(checkpoint_dir.glob("*.jsonl"))
            if checkpoints:
                print(f"   Checkpoint: {checkpoints[0].name}\n")

        elif result["status"] == "completed":
            print("\n✅ Task completed successfully!")
            print(f"   Cycles: {result.get('cycle_count', 'N/A')}")
            print(f"   Result: {result.get('result', 'N/A')}\n")

            # Clean up checkpoint
            for checkpoint in checkpoint_dir.glob("*.jsonl"):
                checkpoint.unlink()
            print("   Checkpoint cleaned up.\n")

        else:
            print(f"\n⚠️  Unknown status: {result['status']}\n")

    except KeyboardInterrupt:
        print("\n⚠️  Immediate shutdown! Checkpoint may be incomplete.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
