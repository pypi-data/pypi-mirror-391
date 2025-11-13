"""
DataFlow persistence backend for conversation memory.

Provides PostgreSQL/SQLite persistence via Kailash DataFlow framework.
Uses workflow-based DataFlow API (NOT ORM-style attribute access).
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from kailash.runtime import LocalRuntime
    from kailash.workflow.builder import WorkflowBuilder

    from dataflow import DataFlow
except ImportError:
    DataFlow = None
    WorkflowBuilder = None
    LocalRuntime = None

logger = logging.getLogger(__name__)


class DataFlowBackend:
    """
    DataFlow backend for conversation persistence.

    Uses DataFlow workflow nodes for database operations.
    Requires ConversationMessage model with these fields:
    - id: str (primary key)
    - conversation_id: str
    - sender: str ("user" or "agent")
    - content: str
    - metadata: dict
    - created_at: datetime (auto-managed)

    Example:
        from dataflow import DataFlow
        from kaizen.memory.backends import DataFlowBackend
        from datetime import datetime

        # Setup DataFlow
        db = DataFlow(db_url="sqlite:///memory.db")

        @db.model
        class ConversationMessage:
            id: str
            conversation_id: str
            sender: str
            content: str
            metadata: dict
            created_at: datetime

        # Use backend
        backend = DataFlowBackend(db, model_name="ConversationMessage")
        backend.save_turn("conv_123", {
            "user": "Hello",
            "agent": "Hi there!",
            "timestamp": "2025-10-25T12:00:00"
        })
    """

    def __init__(self, db: "DataFlow", model_name: str = "ConversationMessage"):
        """
        Initialize DataFlow backend.

        Args:
            db: DataFlow instance (connected to database)
            model_name: Name of the conversation message model class

        Raises:
            ValueError: If DataFlow is not installed
            ValueError: If db is not a DataFlow instance
            ValueError: If required dependencies are missing
        """
        if DataFlow is None or WorkflowBuilder is None or LocalRuntime is None:
            raise ValueError(
                "DataFlow dependencies not installed. "
                "Install with: pip install kailash-dataflow kailash"
            )

        if not isinstance(db, DataFlow):
            raise ValueError(f"Expected DataFlow instance, got {type(db)}")

        self.db = db
        self.model_name = model_name
        self.runtime = LocalRuntime()

        logger.debug(f"Initialized DataFlowBackend with model: {model_name}")

    def save_turn(self, session_id: str, turn: Dict[str, Any]) -> None:
        """
        Save a single conversation turn using DataFlow workflow nodes.

        Creates two message records: one for user, one for agent.

        Note: Empty user/agent messages are allowed (e.g., for acknowledgments).

        Args:
            session_id: Unique session identifier
            turn: Turn data with keys:
                - user: User message (str)
                - agent: Agent response (str)
                - timestamp: ISO format timestamp (str, optional)
                - metadata: Optional metadata (dict)

        Raises:
            Exception: If database save fails
        """
        user_msg = turn.get("user", "")
        agent_msg = turn.get("agent", "")
        metadata = turn.get("metadata", {}) or {}  # Handle None from DataFlow

        # Build workflow to save both messages
        workflow = WorkflowBuilder()

        # Generate unique IDs
        user_msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        agent_msg_id = f"msg_{uuid.uuid4().hex[:12]}"

        # Save user message using ConversationMessageCreateNode
        # NOTE: metadata can be None if using Optional[dict] = None in model
        # BUG FIX: Removed db_instance and model_name - DataFlow nodes don't accept these parameters
        workflow.add_node(
            f"{self.model_name}CreateNode",
            "create_user",
            {
                "id": user_msg_id,
                "conversation_id": session_id,
                "sender": "user",
                "content": user_msg,
                "metadata": metadata if metadata else {},  # Ensure dict, not None
            },
        )

        # Save agent message
        # BUG FIX: Removed db_instance and model_name - DataFlow nodes don't accept these parameters
        workflow.add_node(
            f"{self.model_name}CreateNode",
            "create_agent",
            {
                "id": agent_msg_id,
                "conversation_id": session_id,
                "sender": "agent",
                "content": agent_msg,
                "metadata": metadata if metadata else {},  # Ensure dict, not None
            },
        )

        # Execute workflow
        try:
            results, run_id = self.runtime.execute(workflow.build())
            logger.debug(
                f"Saved turn for session {session_id}: {len(user_msg)} chars user, {len(agent_msg)} chars agent"
            )
        except Exception as e:
            logger.error(f"Failed to save turn: {e}")
            raise

    def load_turns(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Load conversation turns for a session using DataFlow workflow nodes.

        Handles orphaned messages (user without agent or vice versa) by:
        - Logging a warning for orphaned user messages
        - Discarding orphaned user messages (no agent response yet)
        - Ignoring orphaned agent messages (no user message)

        Args:
            session_id: Unique session identifier
            limit: Maximum number of turns to load (None = all)

        Returns:
            List of turns in chronological order (oldest first)
            Each turn contains: user, agent, timestamp, metadata

        Returns:
            Empty list if session not found
        """
        # Build workflow to query messages
        workflow = WorkflowBuilder()

        # Always fetch ALL messages to ensure we can return the LAST N turns
        # (DataFlow default limit is 1000 which should be enough for most cases)
        # BUG FIX: Removed db_instance and model_name - DataFlow nodes don't accept these parameters
        workflow.add_node(
            f"{self.model_name}ListNode",
            "list_messages",
            {
                "filters": {"conversation_id": session_id},
                "limit": 1000,  # Fetch all messages
                "order_by": "created_at",
                "ascending": True,  # Always ASC to preserve user+agent pairing
            },
        )

        # Execute workflow
        try:
            results, run_id = self.runtime.execute(workflow.build())
            messages = results.get("list_messages", {}).get("records", [])
        except Exception as e:
            logger.error(f"Failed to load turns: {e}")
            return []

        # Reconstruct turns from messages
        turns = []
        current_turn = {}

        for msg in messages:
            sender = msg.get("sender")
            content = msg.get("content", "")
            created_at = msg.get("created_at")
            msg_metadata = msg.get("metadata", {})

            if sender == "user":
                # Warn about orphaned user message (if any)
                if current_turn:
                    logger.warning(
                        f"Orphaned user message in session {session_id}: {current_turn.get('user', '')[:50]}"
                    )

                # Start new turn
                current_turn = {
                    "user": content,
                    "timestamp": (
                        created_at
                        if isinstance(created_at, str)
                        else (
                            created_at.isoformat()
                            if created_at
                            else datetime.now().isoformat()
                        )
                    ),
                    "metadata": msg_metadata,
                }
            elif sender == "agent":
                if current_turn:
                    # Complete turn
                    current_turn["agent"] = content
                    turns.append(current_turn)
                    current_turn = {}
                else:
                    # Orphaned agent message (no user message)
                    logger.warning(
                        f"Orphaned agent message in session {session_id}: {content[:50]}"
                    )

        # Check for final orphaned user message
        if current_turn:
            logger.warning(
                f"Incomplete turn in session {session_id}: user message without agent response"
            )

        # Apply limit by returning the LAST N turns (most recent)
        if limit and len(turns) > limit:
            turns = turns[-limit:]

        logger.debug(f"Loaded {len(turns)} turns for session {session_id}")
        return turns

    def clear_session(self, session_id: str) -> None:
        """
        Clear all turns for a session using DataFlow workflow nodes.

        Args:
            session_id: Unique session identifier
        """
        workflow = WorkflowBuilder()

        # Use BulkDeleteNode to delete all messages for session
        # BUG FIX: Removed db_instance - DataFlow nodes don't accept this parameter
        workflow.add_node(
            f"{self.model_name}BulkDeleteNode",
            "delete_messages",
            {"filter": {"conversation_id": session_id}},
        )

        try:
            results, run_id = self.runtime.execute(workflow.build())
            logger.debug(f"Cleared session {session_id}")
        except Exception as e:
            logger.error(f"Failed to clear session: {e}")
            raise

    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session exists using DataFlow workflow nodes.

        Args:
            session_id: Unique session identifier

        Returns:
            True if session has any turns, False otherwise
        """
        workflow = WorkflowBuilder()

        # BUG FIX: Removed db_instance and model_name - DataFlow nodes don't accept these parameters
        workflow.add_node(
            f"{self.model_name}ListNode",
            "check_exists",
            {
                "filters": {"conversation_id": session_id},
                "limit": 1,
            },
        )

        try:
            results, run_id = self.runtime.execute(workflow.build())
            total = results.get("check_exists", {}).get("total", 0)
            return total > 0
        except Exception as e:
            logger.error(f"Failed to check session exists: {e}")
            return False

    def get_session_metadata(self, session_id: str) -> Dict[str, Any]:
        """
        Get metadata about a session using DataFlow workflow nodes.

        Args:
            session_id: Unique session identifier

        Returns:
            Dictionary with keys:
                - turn_count: Total number of turns (int)
                - created_at: First turn timestamp (datetime)
                - updated_at: Last turn timestamp (datetime)

        Returns:
            Empty dict if session not found
        """
        workflow = WorkflowBuilder()

        # BUG FIX: Removed db_instance and model_name - DataFlow nodes don't accept these parameters
        workflow.add_node(
            f"{self.model_name}ListNode",
            "get_metadata",
            {
                "filters": {"conversation_id": session_id},
                "limit": 1000,
                "order_by": "created_at",
                "ascending": True,
            },
        )

        try:
            results, run_id = self.runtime.execute(workflow.build())
            messages = results.get("get_metadata", {}).get("records", [])

            if not messages:
                return {}

            # Count COMPLETE turns (user + agent pairs), matching load_turns() logic
            # Orphaned messages (user without agent or vice versa) are NOT counted
            turn_count = 0
            expecting_user = True

            for msg in messages:
                sender = msg.get("sender")
                if expecting_user and sender == "user":
                    expecting_user = False
                elif not expecting_user and sender == "agent":
                    turn_count += 1
                    expecting_user = True
                else:
                    # Orphaned message - reset state
                    expecting_user = sender != "user"

            first_created = messages[0].get("created_at")
            last_created = messages[-1].get("created_at")

            return {
                "turn_count": turn_count,
                "created_at": first_created,
                "updated_at": last_created,
            }
        except Exception as e:
            logger.error(f"Failed to get session metadata: {e}")
            return {}
