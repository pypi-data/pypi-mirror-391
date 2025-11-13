"""
Example: Auto-stop autonomous agent at budget limit.

This example demonstrates:
1. BudgetHandler for cost-based interruption
2. Real-time cost tracking
3. Graceful shutdown when budget exceeded

Requirements:
- Ollama with llama3.2 model installed

Usage:
    python 03_budget_interrupt.py
"""

import asyncio
from pathlib import Path

from kaizen.agents.autonomous.base import AutonomousConfig, BaseAutonomousAgent
from kaizen.core.autonomy.interrupts.handlers import BudgetInterruptHandler
from kaizen.core.autonomy.interrupts.manager import InterruptManager
from kaizen.core.autonomy.state.manager import StateManager
from kaizen.core.autonomy.state.storage import FilesystemStorage
from kaizen.signatures import InputField, OutputField, Signature


class TaskSignature(Signature):
    """Task signature for autonomous agent."""

    task: str = InputField(description="Task to perform")
    result: str = OutputField(description="Result of task")


async def main():
    """Main execution function."""

    # Setup checkpoint directory
    checkpoint_dir = Path(".kaizen/checkpoints/budget_example")
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Create interrupt manager
    interrupt_manager = InterruptManager()

    # Add budget handler ($0.10 limit for demo)
    MAX_COST = 0.10
    budget_handler = BudgetInterruptHandler(
        interrupt_manager=interrupt_manager, budget_usd=MAX_COST
    )

    print(f"💰 Budget handler configured: ${MAX_COST:.2f} maximum cost\n")

    # Create autonomous agent
    config = AutonomousConfig(
        llm_provider="ollama",
        model="llama3.2",
        temperature=0.7,
        max_cycles=50,  # High limit, budget will stop first
        checkpoint_frequency=1,
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

    print("🚀 Starting autonomous execution with budget tracking...\n")
    print(f"ℹ️  Agent will automatically stop when cost exceeds ${MAX_COST:.2f}.\n")

    # Run autonomous loop (task that will generate costs)
    task = "Write a detailed essay about artificial intelligence"

    try:
        result = await agent._autonomous_loop(task)

        # Check if budget exceeded
        if result["status"] == "interrupted":
            reason = interrupt_manager.get_interrupt_reason()

            if reason and "budget" in reason.message.lower():
                current_cost = budget_handler.get_current_cost()
                print(f"\n💰 Budget limit reached: ${current_cost:.4f}")
                print("   Graceful shutdown completed and checkpoint saved.\n")

                # Show interrupt details
                print(f"   Source: {reason.source.value}")
                print(f"   Mode: {reason.mode.value}")
                print(f"   Message: {reason.message}")
                print(f"   Timestamp: {reason.timestamp}\n")

                # Show cost breakdown
                print("   Cost breakdown:")
                print(f"   - Maximum allowed: ${MAX_COST:.4f}")
                print(f"   - Actual cost: ${current_cost:.4f}")
                print(f"   - Overage: ${current_cost - MAX_COST:.4f}\n")

                # Show checkpoint info
                checkpoints = list(checkpoint_dir.glob("*.jsonl"))
                if checkpoints:
                    print(f"   Checkpoint: {checkpoints[0].name}")
                    print(f"   Cycles completed: {result.get('cycle_count', 'N/A')}\n")
            else:
                print(f"\n⚠️  Interrupted for other reason: {reason.message}\n")

        elif result["status"] == "completed":
            current_cost = budget_handler.get_current_cost()
            print("\n✅ Task completed within budget!\n")
            print(f"   Cycles: {result.get('cycle_count', 'N/A')}")
            print(f"   Cost: ${current_cost:.4f} / ${MAX_COST:.4f}")
            print(f"   Remaining budget: ${MAX_COST - current_cost:.4f}\n")

        else:
            print(f"\n⚠️  Unknown status: {result['status']}\n")

    except Exception as e:
        print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
