"""
BaseAutonomousAgent - Autonomous execution with tool-calling loops.

This module implements the BaseAutonomousAgent class that extends BaseAgent with
autonomous execution capabilities based on Claude Code and Codex research patterns.

Key Features:
1. Single-threaded while(tool_calls_exist) loop (Claude Code pattern)
2. TODO-based planning system for structured task decomposition
3. JSONL checkpoint format for state persistence
4. Objective convergence detection via tool_calls field (ADR-013)
5. Standardized .run() interface for all execution

Architecture:
- Extends BaseAgent with autonomous execution methods
- Uses MultiCycleStrategy for iterative execution
- Supports tool calling with convergence detection
- Optional planning system for complex tasks
- Checkpoint persistence for long-running tasks
- Unified .run() method interface (no execute_autonomously)

References:
- docs/research/CLAUDE_CODE_AUTONOMOUS_ARCHITECTURE.md
- docs/research/CODEX_AUTONOMOUS_ARCHITECTURE.md
- ADR-013: Objective Convergence Detection
- TODO-163: Autonomous Patterns Implementation

Author: Kaizen Framework Team
Created: 2025-10-22
Updated: 2025-10-26 (Standardized to .run() interface)
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from kaizen.core.autonomy.interrupts.manager import InterruptManager
from kaizen.core.autonomy.interrupts.types import (
    InterruptedError,
    InterruptMode,
    InterruptReason,
    InterruptStatus,
)
from kaizen.core.autonomy.state.manager import StateManager
from kaizen.core.autonomy.state.types import AgentState
from kaizen.core.base_agent import BaseAgent
from kaizen.signatures import Signature
from kaizen.strategies.multi_cycle import MultiCycleStrategy

logger = logging.getLogger(__name__)


@dataclass
class AutonomousConfig:
    """
    Configuration for autonomous agent execution.

    This config extends BaseAgentConfig with autonomous-specific parameters:
    - max_cycles: Maximum iteration cycles for autonomous loop
    - planning_enabled: Enable TODO-based planning system
    - checkpoint_frequency: Save state every N cycles

    The config can be automatically converted to BaseAgentConfig using
    BaseAgentConfig.from_domain_config(), enabling seamless integration
    with the BaseAgent architecture.

    Example:
        >>> config = AutonomousConfig(
        ...     max_cycles=20,
        ...     planning_enabled=True,
        ...     checkpoint_frequency=5,
        ...     llm_provider="openai",
        ...     model="gpt-4"
        ... )
        >>> agent = BaseAutonomousAgent(config=config, signature=signature)
    """

    # Autonomous-specific parameters
    max_cycles: int = 20
    planning_enabled: bool = True
    checkpoint_frequency: int = 5

    # State persistence parameters (TODO-168 Day 2)
    resume_from_checkpoint: bool = False  # Resume from latest checkpoint
    checkpoint_interval_seconds: float = 60.0  # Checkpoint every 60 seconds

    # Interrupt parameters (TODO-169 Day 2)
    enable_interrupts: bool = True  # Enable interrupt handling
    graceful_shutdown_timeout: float = 5.0  # Max time for graceful shutdown (seconds)
    checkpoint_on_interrupt: bool = True  # Save checkpoint on interrupt

    # BaseAgentConfig parameters (for conversion)
    llm_provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    provider_config: Optional[Dict[str, Any]] = None

    # Feature flags
    logging_enabled: bool = True
    performance_enabled: bool = False
    error_handling_enabled: bool = True
    batch_processing_enabled: bool = False
    memory_enabled: bool = False
    transparency_enabled: bool = False
    mcp_enabled: bool = False

    # Strategy configuration
    strategy_type: str = "multi_cycle"


class BaseAutonomousAgent(BaseAgent):
    """
    Autonomous agent with tool-calling loops and planning capabilities.

    BaseAutonomousAgent extends BaseAgent with autonomous execution patterns
    inspired by Claude Code and Codex:

    1. **Autonomous Loop**: Single-threaded while(tool_calls_exist) pattern
    2. **Objective Convergence**: Uses tool_calls field for convergence detection
    3. **Planning System**: Optional TODO-based task decomposition
    4. **State Persistence**: JSONL checkpoint format for recovery
    5. **Unified Interface**: .run() method for all execution

    Execution Flow:
        1. create_plan() - Generate structured task list (if enabled)
        2. autonomous_loop() - Execute cycles until convergence:
           a. gather_context() - Collect current state
           b. take_action() - Execute LLM + tools
           c. verify() - Check convergence via tool_calls
           d. iterate() - Continue or terminate
        3. save_checkpoint() - Persist state (at specified frequency)

    Convergence Detection (ADR-013):
        - **Objective** (preferred): Check tool_calls field
          - Empty list [] → converged
          - Non-empty list → not converged
        - **Subjective** (fallback): Action-based detection
          - action == "finish" → converged
          - confidence > threshold → converged

    Example:
        >>> from kaizen.agents.autonomous.base import BaseAutonomousAgent, AutonomousConfig
        >>>
        >>> config = AutonomousConfig(
        ...     max_cycles=15,
        ...     planning_enabled=True,
        ...     llm_provider="openai",
        ...     model="gpt-4"
        ... )
        >>>
        >>> agent = BaseAutonomousAgent(
        ...     config=config,
        ...     signature=TaskSignature()
        ... )
        >>>
        >>> # Use .run() method (standard interface)
        >>> result = agent.run(task="Build API integration")
        >>> print(f"Completed in {result['cycles_used']} cycles")

    Notes:
        - Uses MultiCycleStrategy for cycle management
        - MCP integration for autonomous tool use
        - Planning is optional (can be disabled for simple tasks)
        - Checkpoints enable recovery from failures
        - Uses .run() for consistency with other BaseAgent subclasses
    """

    def __init__(
        self,
        config: AutonomousConfig,
        signature: Optional[Signature] = None,
        strategy: Optional[MultiCycleStrategy] = None,
        checkpoint_dir: Optional[Path] = None,
        state_manager: Optional[StateManager] = None,
        interrupt_manager: Optional[InterruptManager] = None,
        **kwargs,
    ):
        """
        Initialize BaseAutonomousAgent with autonomous execution capabilities.

        Args:
            config: AutonomousConfig with autonomous-specific parameters
            signature: Optional signature (uses _default_signature() if None)
            strategy: Optional MultiCycleStrategy (creates default if None)
            checkpoint_dir: Optional directory for checkpoint persistence
            state_manager: Optional StateManager for checkpoint operations (TODO-168)
            interrupt_manager: Optional InterruptManager for interrupt handling (TODO-169)
            **kwargs: Additional arguments passed to BaseAgent.__init__ (including mcp_servers)

        Example:
            >>> config = AutonomousConfig(max_cycles=20, planning_enabled=True)
            >>> agent = BaseAutonomousAgent(
            ...     config=config,
            ...     signature=signature
            ... )
        """
        # Store original autonomous config
        self.autonomous_config = config

        # Create MultiCycleStrategy with convergence detection
        if strategy is None:
            strategy = MultiCycleStrategy(
                max_cycles=config.max_cycles,
                convergence_check=self._check_convergence,
            )

        # Initialize BaseAgent (will auto-convert config to BaseAgentConfig)
        # Tool calling is handled via MCP integration (pass mcp_servers in kwargs if needed)
        super().__init__(
            config=config,
            signature=signature,
            strategy=strategy,
            **kwargs,
        )

        # Autonomous-specific state
        self.checkpoint_dir = checkpoint_dir or Path("./checkpoints")
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.current_plan: List[Dict[str, Any]] = []
        self.cycle_count: int = 0

        # State persistence (TODO-168)
        self.state_manager = state_manager or StateManager(
            checkpoint_frequency=config.checkpoint_frequency,
            checkpoint_interval=config.checkpoint_interval_seconds,  # StateManager uses 'checkpoint_interval'
        )
        self.current_step: int = 0

        # Interrupt management (TODO-169)
        self.interrupt_manager = interrupt_manager or InterruptManager()

        # Install signal handlers if interrupts enabled
        if config.enable_interrupts:
            self.interrupt_manager.install_signal_handlers()
            # Register shutdown callback
            self.interrupt_manager.register_shutdown_callback(self._on_shutdown)

    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute autonomous task with .run() interface.

        This is the standardized entry point for all BaseAgent subclasses.
        Executes a task autonomously using the following flow:
        1. Create plan (if planning enabled)
        2. Run autonomous loop until convergence
        3. Return results with metadata

        Args:
            **kwargs: Task inputs matching signature (typically 'task' field)

        Returns:
            Dict with execution results, including:
            - result: Final task result
            - cycles_used: Number of cycles executed
            - total_cycles: Maximum cycles allowed
            - plan: Task plan (if planning enabled)
            - checkpoints: List of checkpoint files created

        Example:
            >>> # Standard .run() interface
            >>> result = agent.run(task="Analyze sales data and generate report")
            >>> print(f"Task completed in {result['cycles_used']} cycles")
            >>> print(f"Result: {result['result']}")

        Raises:
            ValueError: If task is empty or invalid
            RuntimeError: If execution fails critically
        """
        # Extract task from kwargs (signature-based input)
        task = kwargs.get("task")
        if not task or not isinstance(task, str) or not task.strip():
            raise ValueError("Task cannot be empty (provide task='...' argument)")

        logger.info(f"Starting autonomous execution: {task}")

        # Step 1: Create plan (if enabled)
        if self.autonomous_config.planning_enabled:
            logger.info("Creating execution plan...")
            import asyncio

            self.current_plan = asyncio.run(self._create_plan(task))
            logger.info(f"Plan created with {len(self.current_plan)} tasks")
        else:
            self.current_plan = []

        # Step 2: Execute autonomous loop
        logger.info("Starting autonomous loop...")
        import asyncio

        result = asyncio.run(self._autonomous_loop(task))

        # Step 3: Add metadata
        result["plan"] = self.current_plan if self.current_plan else []
        result["task"] = task

        logger.info(
            f"Autonomous execution completed in {result.get('cycles_used', 0)} cycles"
        )

        return result

    async def _autonomous_loop(self, task: str) -> Dict[str, Any]:
        """
        Autonomous execution loop following while(tool_calls_exist) pattern.

        This implements the Claude Code autonomous loop:
        1. Resume from checkpoint (if enabled) (TODO-168 Day 2)
        2. Execute cycle (LLM reasoning + tool calls)
        3. Check convergence via tool_calls field
        4. Continue if tool_calls exist, exit if empty
        5. Enforce max_cycles limit
        6. Save checkpoints at frequency/interval (TODO-168 Day 2)
        7. Check for interrupts before each cycle (TODO-169 Day 1)

        Args:
            task: Task to execute

        Returns:
            Dict with final result and metadata

        Raises:
            InterruptedError: When execution is interrupted

        Example:
            >>> result = await agent._autonomous_loop("Search and summarize")
            >>> if result.get('tool_calls') == []:
            ...     print("Task converged successfully")
        """
        # TODO-168 Day 2: Resume from checkpoint if enabled
        if self.autonomous_config.resume_from_checkpoint:
            agent_id = (
                self.config.name if hasattr(self.config, "name") else "autonomous_agent"
            )
            resumed_state = await self.state_manager.resume_from_latest(agent_id)
            if resumed_state:
                self._restore_state(resumed_state)
                logger.info(f"Resumed from checkpoint at step {self.current_step}")
            else:
                logger.info("No checkpoint found, starting fresh")

        self.cycle_count = 0
        final_result = {}

        # Prepare initial inputs
        inputs = {"task": task}
        if self.current_plan:
            inputs["plan"] = self.current_plan

        # Autonomous loop: while(tool_calls_exist)
        for cycle_num in range(self.autonomous_config.max_cycles):
            # TODO-169 Day 1: Check for interrupt BEFORE cycle
            if self.interrupt_manager.is_interrupted():
                reason = self.interrupt_manager._interrupt_reason

                if reason.mode == InterruptMode.GRACEFUL:
                    logger.info(
                        "Graceful interrupt requested, finishing current cycle..."
                    )
                    # Finish current cycle
                    try:
                        cycle_result = self.strategy.execute(self, inputs)
                        final_result = cycle_result
                    except Exception as e:
                        logger.warning(f"Error during graceful shutdown cycle: {e}")
                        final_result = {
                            "error": str(e),
                            "status": "interrupted",
                            "cycle": self.cycle_count,
                        }
                else:  # IMMEDIATE
                    logger.warning("Immediate interrupt requested, stopping now...")
                    final_result = {
                        "status": "interrupted",
                        "cycle": self.cycle_count,
                        "message": "Execution interrupted immediately",
                    }

                # Save checkpoint before shutdown
                await self._save_final_checkpoint(interrupted=True, reason=reason)

                # Execute shutdown callbacks
                await self.interrupt_manager.execute_shutdown_callbacks()

                # Raise InterruptedError to exit loop
                raise InterruptedError(reason.message, reason=reason)

            self.cycle_count = cycle_num + 1

            try:
                logger.debug(
                    f"Cycle {self.cycle_count}/{self.autonomous_config.max_cycles}"
                )

                # Execute cycle using strategy
                cycle_result = self.strategy.execute(self, inputs)

                # TODO-168 Day 2: Increment step counter
                self.current_step += 1

                # TODO-168 Day 2: Save checkpoint if needed (frequency OR interval)
                import time

                if self.state_manager.should_checkpoint(
                    agent_id=(
                        self.config.name
                        if hasattr(self.config, "name")
                        else "autonomous_agent"
                    ),
                    current_step=self.current_step,
                    current_time=time.time(),
                ):
                    state = self._capture_state()
                    checkpoint_id = await self.state_manager.save_checkpoint(state)
                    logger.info(
                        f"Checkpoint saved: {checkpoint_id} (step={self.current_step})"
                    )

                # Check convergence (objective via tool_calls)
                if self._check_convergence(cycle_result):
                    logger.info(f"Converged at cycle {self.cycle_count}")
                    final_result = cycle_result
                    break

                # Update inputs for next cycle
                if "observation" in cycle_result:
                    inputs["observation"] = cycle_result["observation"]

            except Exception as e:
                logger.error(f"Error in cycle {self.cycle_count}: {e}")
                final_result = {
                    "error": str(e),
                    "status": "failed",
                    "cycle": self.cycle_count,
                }
                break

        # Add cycle metadata
        final_result["cycles_used"] = self.cycle_count
        final_result["total_cycles"] = self.autonomous_config.max_cycles

        # TODO-169 Day 1: Save final checkpoint (normal completion)
        await self._save_final_checkpoint(interrupted=False, reason=None)

        return final_result

    def _check_convergence(self, response: Dict[str, Any]) -> bool:
        """
        Check if agent has converged using objective detection (ADR-013).

        Convergence Detection Priority:
        1. **Objective** (preferred): Check tool_calls field
           - Empty list [] → converged
           - Non-empty list → not converged
           - Missing/None → fall back to subjective

        2. **Subjective** (fallback): Action-based detection
           - action == "finish" → converged
           - confidence > 0.9 → converged
           - Default → True (safe convergence)

        Args:
            response: LLM response to check for convergence

        Returns:
            bool: True if converged (stop iteration), False if not (continue)

        Example:
            >>> response = {"result": "Done", "tool_calls": []}
            >>> converged = agent._check_convergence(response)
            >>> assert converged is True

            >>> response = {"result": "Need tool", "tool_calls": [{"name": "search"}]}
            >>> converged = agent._check_convergence(response)
            >>> assert converged is False
        """
        # OBJECTIVE DETECTION (preferred): Check tool_calls field
        if "tool_calls" in response:
            tool_calls = response.get("tool_calls")

            # Handle None case
            if tool_calls is None:
                logger.debug("tool_calls is None, falling back to subjective")
            # Check if tool_calls is a list
            elif isinstance(tool_calls, list):
                # Empty list = converged
                if not tool_calls:
                    logger.debug("Objective convergence: tool_calls is empty")
                    return True
                # Non-empty list = not converged
                else:
                    logger.debug(
                        f"Objective non-convergence: {len(tool_calls)} tool_calls"
                    )
                    return False
            # Malformed tool_calls (not a list)
            else:
                logger.warning(
                    f"Malformed tool_calls field (type: {type(tool_calls)}), falling back"
                )

        # SUBJECTIVE DETECTION (fallback): Action-based detection
        logger.debug("Using subjective convergence detection")

        # Check for finish action
        action = response.get("action", "")
        if action == "finish":
            logger.debug("Subjective convergence: action == 'finish'")
            return True

        # Check for high confidence
        confidence = response.get("confidence", 0.0)
        if confidence > 0.9:
            logger.debug(f"Subjective convergence: confidence = {confidence}")
            return True

        # Default: converged (safe fallback when no clear signals)
        logger.debug("Default convergence: no clear signals")
        return True

    async def _create_plan(self, task: str) -> List[Dict[str, Any]]:
        """
        Generate TODO-style structured task plan.

        Uses LLM to decompose the task into a list of subtasks with
        TODO-style structure (task, status, priority, etc.).

        Args:
            task: Task to create plan for

        Returns:
            List of task dictionaries with TODO structure:
            - task: Task description
            - status: "pending", "in_progress", or "completed"
            - priority: "low", "medium", or "high"
            - estimated_cycles: Estimated cycles needed

        Example:
            >>> plan = await agent._create_plan("Build REST API")
            >>> print(plan)
            [
                {"task": "Design API schema", "status": "pending", "priority": "high"},
                {"task": "Implement endpoints", "status": "pending", "priority": "high"},
                {"task": "Write tests", "status": "pending", "priority": "medium"}
            ]
        """
        # If planning is disabled, return empty plan
        if not self.autonomous_config.planning_enabled:
            return []

        # Generate plan from LLM
        plan = await self._generate_plan_from_llm(task)
        return plan

    async def _generate_plan_from_llm(self, task: str) -> List[Dict[str, Any]]:
        """
        Use LLM to generate a structured task plan.

        This is a placeholder that will use the LLM to decompose
        the task into subtasks. For now, returns a simple plan structure.

        Args:
            task: Task to plan

        Returns:
            List of task dictionaries

        Note:
            Full LLM integration will be added in future enhancement.
            Current implementation provides basic structure.
        """
        # TODO: Implement full LLM-based planning
        # For now, return simple plan structure
        return [
            {
                "task": f"Execute: {task}",
                "status": "pending",
                "priority": "high",
                "estimated_cycles": 5,
            }
        ]

    def _save_checkpoint(self, state: Dict[str, Any], cycle_num: int) -> None:
        """
        Save execution checkpoint in JSONL format.

        Checkpoints enable recovery from failures and provide audit trail.
        Saved in JSONL format (one JSON object per line) for easy parsing.

        Args:
            state: Current execution state
            cycle_num: Current cycle number

        Example:
            >>> agent._save_checkpoint(result, cycle_num=5)
            # Saves to: ./checkpoints/task_<timestamp>_cycle_5.jsonl
        """
        checkpoint_file = (
            self.checkpoint_dir / f"checkpoint_cycle_{cycle_num:03d}.jsonl"
        )

        checkpoint_data = {
            "cycle": cycle_num,
            "state": state,
            "plan": self.current_plan,
        }

        try:
            with open(checkpoint_file, "a") as f:
                f.write(json.dumps(checkpoint_data) + "\n")

            logger.debug(f"Checkpoint saved: {checkpoint_file}")
        except Exception as e:
            logger.warning(f"Failed to save checkpoint: {e}")

    def _load_checkpoint(self, cycle_num: int) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint from JSONL file.

        Args:
            cycle_num: Cycle number to load

        Returns:
            Checkpoint data or None if not found

        Example:
            >>> state = agent._load_checkpoint(cycle_num=5)
            >>> if state:
            ...     print(f"Restored from cycle {state['cycle']}")
        """
        checkpoint_file = (
            self.checkpoint_dir / f"checkpoint_cycle_{cycle_num:03d}.jsonl"
        )

        if not checkpoint_file.exists():
            return None

        try:
            with open(checkpoint_file, "r") as f:
                # Read last line (most recent checkpoint)
                lines = f.readlines()
                if lines:
                    return json.loads(lines[-1])
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")

        return None

    # ═══════════════════════════════════════════════════════════════
    # State Persistence (TODO-168)
    # ═══════════════════════════════════════════════════════════════

    def _capture_state(self) -> AgentState:
        """
        Capture current agent state for checkpoint (TODO-168).

        Returns:
            AgentState containing complete agent state snapshot

        Example:
            >>> state = agent._capture_state()
            >>> print(f"Captured state at step {state.step_number}")
        """
        return AgentState(
            agent_id=(
                self.config.name if hasattr(self.config, "name") else "autonomous_agent"
            ),
            step_number=self.current_step,
            conversation_history=self._get_conversation_history(),
            memory_contents=self._get_memory_contents(),
            pending_actions=self._get_pending_actions(),
            completed_actions=self._get_completed_actions(),
            budget_spent_usd=self._get_budget_spent(),
            approval_history=self._get_approval_history(),
            tool_usage_counts=self._get_tool_usage_counts(),
            workflow_run_id=getattr(self, "_workflow_run_id", None),
            workflow_state=self._get_workflow_state(),
        )

    def _restore_state(self, state: AgentState) -> None:
        """
        Restore agent from checkpoint state (TODO-168).

        Args:
            state: AgentState to restore from

        Example:
            >>> state = await agent.state_manager.resume_from_latest("my_agent")
            >>> if state:
            ...     agent._restore_state(state)
            ...     print(f"Resumed from step {agent.current_step}")
        """
        self.current_step = state.step_number
        self._restore_conversation_history(state.conversation_history)
        self._restore_memory_contents(state.memory_contents)
        self._restore_pending_actions(state.pending_actions)
        self._restore_completed_actions(state.completed_actions)
        # Budget and approval history restoration handled by permission system
        # Tool usage counts and workflow state restored as needed

        logger.info(
            f"State restored from checkpoint {state.checkpoint_id} "
            f"(step={state.step_number})"
        )

    # Helper methods for state capture

    def _get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history for checkpoint."""
        if self.memory is not None:
            # Extract conversation from memory
            return [
                {"role": msg.role, "content": msg.content}
                for msg in getattr(self.memory, "messages", [])
            ]
        return []

    def _get_memory_contents(self) -> Dict[str, Any]:
        """Get memory contents for checkpoint."""
        if self.memory is not None:
            return {
                "message_count": len(getattr(self.memory, "messages", [])),
                "metadata": getattr(self.memory, "metadata", {}),
            }
        return {}

    def _get_pending_actions(self) -> List[Dict[str, Any]]:
        """Get pending actions for checkpoint."""
        # Extract from current_plan if available
        if self.current_plan:
            return [
                action
                for action in self.current_plan
                if action.get("status") == "pending"
            ]
        return []

    def _get_completed_actions(self) -> List[Dict[str, Any]]:
        """Get completed actions for checkpoint."""
        if self.current_plan:
            return [
                action
                for action in self.current_plan
                if action.get("status") == "completed"
            ]
        return []

    def _get_budget_spent(self) -> float:
        """Get budget spent for checkpoint."""
        if hasattr(self, "execution_context"):
            return self.execution_context.budget_used
        return 0.0

    def _get_approval_history(self) -> List[Dict[str, Any]]:
        """Get approval history for checkpoint."""
        # TODO: Extract from approval manager once implemented
        return []

    def _get_tool_usage_counts(self) -> Dict[str, int]:
        """Get tool usage counts for checkpoint."""
        # TODO: Implement tool usage tracking
        return {}

    def _get_workflow_state(self) -> Dict[str, Any]:
        """Get workflow execution state for checkpoint."""
        # TODO: Extract from Kailash SDK runtime
        return {}

    # Helper methods for state restoration

    def _restore_conversation_history(
        self, conversation_history: List[Dict[str, Any]]
    ) -> None:
        """Restore conversation history from checkpoint."""
        if self.memory is not None and conversation_history:
            # Clear existing messages
            if hasattr(self.memory, "messages"):
                self.memory.messages.clear()

            # Restore messages
            for msg in conversation_history:
                self.memory.add_message(
                    role=msg.get("role", "user"), content=msg.get("content", "")
                )

    def _restore_memory_contents(self, memory_contents: Dict[str, Any]) -> None:
        """Restore memory contents from checkpoint."""
        if self.memory is not None and memory_contents:
            # Restore metadata
            if "metadata" in memory_contents:
                self.memory.metadata = memory_contents["metadata"]

    def _restore_pending_actions(self, pending_actions: List[Dict[str, Any]]) -> None:
        """Restore pending actions from checkpoint."""
        # Update current_plan with pending actions
        for action in pending_actions:
            if action not in self.current_plan:
                self.current_plan.append(action)

    def _restore_completed_actions(
        self, completed_actions: List[Dict[str, Any]]
    ) -> None:
        """Restore completed actions from checkpoint."""
        # Update current_plan with completed actions
        for action in completed_actions:
            if action not in self.current_plan:
                self.current_plan.append(action)

    # ═══════════════════════════════════════════════════════════════
    # Interrupt Management (TODO-169)
    # ═══════════════════════════════════════════════════════════════

    async def _on_shutdown(self) -> None:
        """
        Shutdown callback for graceful cleanup (TODO-169).

        Called by InterruptManager before shutdown to release resources
        and close connections. Registered in __init__.

        Example:
            >>> # Called automatically when interrupt detected
            >>> await agent.interrupt_manager.execute_shutdown_callbacks()
        """
        logger.info("Executing shutdown cleanup...")

        # Close HTTP client if exists
        if hasattr(self, "_http_client"):
            try:
                await self._http_client.close()
                logger.debug("HTTP client closed")
            except Exception as e:
                logger.warning(f"Error closing HTTP client: {e}")

        # Close MCP connections if exists
        if hasattr(self, "_mcp_clients"):
            for client_name, client in self._mcp_clients.items():
                try:
                    await client.close()
                    logger.debug(f"MCP client '{client_name}' closed")
                except Exception as e:
                    logger.warning(f"Error closing MCP client '{client_name}': {e}")

        # Release any other resources
        # (Add more cleanup as needed)

        logger.info("Shutdown cleanup complete")

    async def _handle_interrupt(self) -> InterruptStatus:
        """
        Handle interrupt with graceful or immediate mode (TODO-169 Day 2).

        Executes shutdown sequence based on interrupt mode:
        - GRACEFUL: Execute shutdown callbacks, save checkpoint, allow current step to finish
        - IMMEDIATE: Save checkpoint if possible, stop immediately

        Returns:
            InterruptStatus with checkpoint information

        Raises:
            InterruptedError: If execution should stop

        Example:
            >>> # Called automatically when interrupt detected in autonomous loop
            >>> if self.interrupt_manager.is_interrupted():
            ...     status = await self._handle_interrupt()
            ...     raise InterruptedError(status.reason)
        """
        if not self.interrupt_manager.is_interrupted():
            return InterruptStatus(interrupted=False)

        reason = self.interrupt_manager.get_interrupt_reason()
        logger.warning(
            f"Handling interrupt: {reason.message} (mode={reason.mode.value})"
        )

        # Determine checkpoint behavior
        should_checkpoint = self.autonomous_config.checkpoint_on_interrupt

        # Prepare agent state for checkpointing
        agent_state = None
        if should_checkpoint:
            agent_state = self._capture_state()

        # Handle based on mode
        if reason.mode == InterruptMode.GRACEFUL:
            # Graceful: Execute shutdown callbacks first
            logger.info("Executing graceful shutdown...")

            # Execute shutdown with timeout
            try:
                timeout = self.autonomous_config.graceful_shutdown_timeout
                async with asyncio.timeout(timeout):
                    status = await self.interrupt_manager.execute_shutdown(
                        state_manager=self.state_manager if should_checkpoint else None,
                        agent_state=agent_state,
                    )
                logger.info(
                    f"Graceful shutdown completed: checkpoint={status.checkpoint_id}"
                )
                return status

            except asyncio.TimeoutError:
                logger.warning(
                    f"Graceful shutdown timed out after {timeout}s, forcing immediate shutdown"
                )
                # Fall through to immediate shutdown

        # Immediate shutdown (or graceful timeout)
        logger.info("Executing immediate shutdown...")

        # Try to save checkpoint quickly
        checkpoint_id = None
        if should_checkpoint and agent_state:
            try:
                # Mark state as interrupted
                agent_state.status = "interrupted"
                agent_state.metadata["interrupt_reason"] = reason.to_dict()

                # Save checkpoint with short timeout
                checkpoint_id = await self.state_manager.save_checkpoint(
                    agent_state, force=True
                )
                logger.info(f"Emergency checkpoint saved: {checkpoint_id}")

            except Exception as e:
                logger.error(f"Failed to save emergency checkpoint: {e}", exc_info=True)

        # Create interrupt status
        status = InterruptStatus(
            interrupted=True, reason=reason, checkpoint_id=checkpoint_id
        )

        logger.info("Immediate shutdown completed")
        return status

    def register_child_agent(self, child_agent: "BaseAutonomousAgent") -> None:
        """
        Register child agent for interrupt propagation (TODO-169 Day 3).

        When this agent is interrupted, the interrupt will propagate to all
        registered child agents. This is useful for multi-agent scenarios where
        a supervisor coordinates multiple workers.

        Args:
            child_agent: Child BaseAutonomousAgent to track

        Example:
            >>> supervisor = SupervisorAgent(config=config, signature=signature)
            >>> worker1 = WorkerAgent(config=config, signature=signature)
            >>> worker2 = WorkerAgent(config=config, signature=signature)
            >>>
            >>> # Register workers as children
            >>> supervisor.register_child_agent(worker1)
            >>> supervisor.register_child_agent(worker2)
            >>>
            >>> # When supervisor is interrupted, workers are interrupted too
            >>> supervisor.interrupt_manager.request_interrupt(...)
            >>> supervisor.interrupt_manager.propagate_to_children()
        """
        if hasattr(child_agent, "interrupt_manager"):
            self.interrupt_manager.add_child_manager(child_agent.interrupt_manager)
            logger.debug(f"Registered child agent: {child_agent.agent_id}")
        else:
            logger.warning(
                f"Child agent {child_agent.agent_id} has no interrupt_manager, skipping registration"
            )

    def unregister_child_agent(self, child_agent: "BaseAutonomousAgent") -> None:
        """
        Unregister child agent from interrupt propagation (TODO-169 Day 3).

        Args:
            child_agent: Child BaseAutonomousAgent to remove

        Example:
            >>> supervisor.unregister_child_agent(worker1)
        """
        if hasattr(child_agent, "interrupt_manager"):
            self.interrupt_manager.remove_child_manager(child_agent.interrupt_manager)
            logger.debug(f"Unregistered child agent: {child_agent.agent_id}")

    async def _save_final_checkpoint(
        self, interrupted: bool = False, reason: Optional[InterruptReason] = None
    ) -> str:
        """
        Save final checkpoint with interrupt metadata (TODO-169).

        Args:
            interrupted: Whether execution was interrupted
            reason: InterruptReason if interrupted

        Returns:
            Checkpoint ID

        Example:
            >>> # Normal completion
            >>> checkpoint_id = await agent._save_final_checkpoint(interrupted=False)
            >>>
            >>> # Interrupted completion
            >>> checkpoint_id = await agent._save_final_checkpoint(
            ...     interrupted=True,
            ...     reason=interrupt_reason
            ... )
        """
        state = self._capture_state()

        if interrupted:
            state.status = "interrupted"
            if reason:
                state.metadata["interrupt_reason"] = {
                    "source": reason.source.value,
                    "mode": reason.mode.value,
                    "message": reason.message,
                    "timestamp": reason.timestamp.isoformat(),
                    "metadata": reason.metadata,
                }
                logger.info(
                    f"Saving final checkpoint with interrupt reason: {reason.message}"
                )
        else:
            # Normal completion - determine status from current state
            if "error" in getattr(self, "_last_result", {}):
                state.status = "failed"
            else:
                state.status = "completed"

        checkpoint_id = await self.state_manager.save_checkpoint(state, force=True)
        logger.info(f"Final checkpoint saved: {checkpoint_id} (status={state.status})")

        return checkpoint_id
