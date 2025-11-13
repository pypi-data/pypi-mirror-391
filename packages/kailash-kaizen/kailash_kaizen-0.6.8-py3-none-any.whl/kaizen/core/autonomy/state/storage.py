"""
Storage backends for checkpoint persistence.

Provides protocol for storage backends and filesystem implementation.
"""

import gzip
import json
import logging
import shutil
import tempfile
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Protocol, runtime_checkable

from .types import AgentState, CheckpointMetadata

logger = logging.getLogger(__name__)


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol for checkpoint storage backends"""

    @abstractmethod
    async def save(self, state: AgentState) -> str:
        """
        Save checkpoint and return checkpoint_id.

        Args:
            state: Agent state to checkpoint

        Returns:
            checkpoint_id of saved checkpoint

        Raises:
            IOError: If save fails
        """
        ...

    @abstractmethod
    async def load(self, checkpoint_id: str) -> AgentState:
        """
        Load checkpoint by ID.

        Args:
            checkpoint_id: ID of checkpoint to load

        Returns:
            AgentState restored from checkpoint

        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        ...

    @abstractmethod
    async def list_checkpoints(
        self, agent_id: str | None = None
    ) -> list[CheckpointMetadata]:
        """
        List all checkpoints (optionally filtered by agent_id).

        Args:
            agent_id: Filter checkpoints for specific agent (None = all)

        Returns:
            List of checkpoint metadata sorted by timestamp (newest first)
        """
        ...

    @abstractmethod
    async def delete(self, checkpoint_id: str) -> None:
        """
        Delete checkpoint.

        Args:
            checkpoint_id: ID of checkpoint to delete

        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        ...

    @abstractmethod
    async def exists(self, checkpoint_id: str) -> bool:
        """
        Check if checkpoint exists.

        Args:
            checkpoint_id: ID of checkpoint

        Returns:
            True if checkpoint exists
        """
        ...


class FilesystemStorage:
    """
    Filesystem-based checkpoint storage (JSONL format).

    Stores checkpoints as JSONL files with atomic writes and compression support.
    """

    def __init__(
        self,
        base_dir: str | Path = ".kaizen/checkpoints",
        compress: bool = False,
    ):
        """
        Initialize filesystem storage.

        Args:
            base_dir: Directory for checkpoint storage
            compress: Whether to compress checkpoints (gzip)
        """
        self.base_dir = Path(base_dir)
        self.compress = compress

        # Create directory if it doesn't exist
        self.base_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Filesystem storage initialized: {self.base_dir}")

    async def save(self, state: AgentState) -> str:
        """
        Save checkpoint as JSONL file with atomic write (TODO-168 Day 3).

        Uses temp file + rename for atomicity.
        Supports gzip compression for smaller checkpoint files.

        Args:
            state: Agent state to checkpoint

        Returns:
            checkpoint_id

        Raises:
            IOError: If save fails
        """
        # Determine file extension based on compression
        file_ext = ".jsonl.gz" if self.compress else ".jsonl"
        checkpoint_path = self.base_dir / f"{state.checkpoint_id}{file_ext}"

        tmp_path = None
        try:
            # Convert state to dict
            state_dict = state.to_dict()
            json_str = json.dumps(state_dict) + "\n"

            if self.compress:
                # Write compressed (gzip)
                with tempfile.NamedTemporaryFile(
                    mode="wb", dir=self.base_dir, delete=False, suffix=".tmp"
                ) as tmp_file:
                    tmp_path = Path(tmp_file.name)
                    tmp_file.write(gzip.compress(json_str.encode("utf-8")))
            else:
                # Write uncompressed
                with tempfile.NamedTemporaryFile(
                    mode="w", dir=self.base_dir, delete=False, suffix=".tmp"
                ) as tmp_file:
                    tmp_path = Path(tmp_file.name)
                    tmp_file.write(json_str)

            # Atomic rename
            shutil.move(str(tmp_path), str(checkpoint_path))

            size_bytes = checkpoint_path.stat().st_size
            compression_status = "compressed" if self.compress else "uncompressed"
            logger.info(
                f"Checkpoint saved: {state.checkpoint_id} "
                f"({size_bytes} bytes, {compression_status})"
            )

            return state.checkpoint_id

        except Exception as e:
            logger.error(f"Failed to save checkpoint {state.checkpoint_id}: {e}")
            # Clean up temp file if it exists
            if tmp_path and tmp_path.exists():
                tmp_path.unlink()
            raise IOError(f"Failed to save checkpoint: {e}")

    async def load(self, checkpoint_id: str) -> AgentState:
        """
        Load checkpoint from JSONL file (TODO-168 Day 3).

        Auto-detects compression by checking for .gz extension.

        Args:
            checkpoint_id: ID of checkpoint to load

        Returns:
            AgentState restored from checkpoint

        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        # Try compressed version first, then uncompressed
        compressed_path = self.base_dir / f"{checkpoint_id}.jsonl.gz"
        uncompressed_path = self.base_dir / f"{checkpoint_id}.jsonl"

        checkpoint_path = None
        is_compressed = False

        if compressed_path.exists():
            checkpoint_path = compressed_path
            is_compressed = True
        elif uncompressed_path.exists():
            checkpoint_path = uncompressed_path
            is_compressed = False
        else:
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")

        try:
            if is_compressed:
                # Load compressed (gzip)
                with gzip.open(checkpoint_path, "rt", encoding="utf-8") as f:
                    state_dict = json.loads(f.read().strip())
            else:
                # Load uncompressed
                with open(checkpoint_path, "r") as f:
                    state_dict = json.loads(f.read().strip())

            state = AgentState.from_dict(state_dict)
            compression_status = "compressed" if is_compressed else "uncompressed"
            logger.info(f"Checkpoint loaded: {checkpoint_id} ({compression_status})")

            return state

        except Exception as e:
            logger.error(f"Failed to load checkpoint {checkpoint_id}: {e}")
            raise IOError(f"Failed to load checkpoint: {e}")

    async def list_checkpoints(
        self, agent_id: str | None = None
    ) -> list[CheckpointMetadata]:
        """
        List all checkpoints in directory (TODO-168 Day 3).

        Auto-detects compressed and uncompressed checkpoints.

        Args:
            agent_id: Filter checkpoints for specific agent (None = all)

        Returns:
            List of checkpoint metadata sorted by timestamp (newest first)
        """
        checkpoints = []

        try:
            # Check both compressed and uncompressed files
            for pattern in ["*.jsonl.gz", "*.jsonl"]:
                for path in self.base_dir.glob(pattern):
                    # Read checkpoint to get metadata
                    try:
                        is_compressed = path.suffix == ".gz"

                        if is_compressed:
                            # Load compressed (gzip)
                            with gzip.open(path, "rt", encoding="utf-8") as f:
                                state_dict = json.loads(f.read().strip())
                        else:
                            # Load uncompressed
                            with open(path, "r") as f:
                                state_dict = json.loads(f.read().strip())

                        # Filter by agent_id if specified
                        if agent_id and state_dict.get("agent_id") != agent_id:
                            continue

                        # Parse timestamp
                        timestamp_str = state_dict["timestamp"]
                        if isinstance(timestamp_str, str):
                            timestamp = datetime.fromisoformat(timestamp_str)
                        else:
                            timestamp = timestamp_str

                        metadata = CheckpointMetadata(
                            checkpoint_id=state_dict["checkpoint_id"],
                            agent_id=state_dict["agent_id"],
                            timestamp=timestamp,
                            step_number=state_dict["step_number"],
                            status=state_dict["status"],
                            size_bytes=path.stat().st_size,
                            parent_checkpoint_id=state_dict.get("parent_checkpoint_id"),
                        )
                        checkpoints.append(metadata)

                    except Exception as e:
                        logger.warning(f"Failed to read checkpoint {path.name}: {e}")
                        continue

            # Sort by timestamp (newest first)
            checkpoints.sort(key=lambda c: c.timestamp, reverse=True)

            return checkpoints

        except Exception as e:
            logger.error(f"Failed to list checkpoints: {e}")
            return []

    async def delete(self, checkpoint_id: str) -> None:
        """
        Delete checkpoint file (TODO-168 Day 3).

        Auto-detects compressed and uncompressed checkpoints.

        Args:
            checkpoint_id: ID of checkpoint to delete

        Raises:
            FileNotFoundError: If checkpoint doesn't exist
        """
        # Try compressed version first, then uncompressed
        compressed_path = self.base_dir / f"{checkpoint_id}.jsonl.gz"
        uncompressed_path = self.base_dir / f"{checkpoint_id}.jsonl"

        checkpoint_path = None
        if compressed_path.exists():
            checkpoint_path = compressed_path
        elif uncompressed_path.exists():
            checkpoint_path = uncompressed_path
        else:
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_id}")

        try:
            checkpoint_path.unlink()
            logger.info(f"Checkpoint deleted: {checkpoint_id}")

        except Exception as e:
            logger.error(f"Failed to delete checkpoint {checkpoint_id}: {e}")
            raise IOError(f"Failed to delete checkpoint: {e}")

    async def exists(self, checkpoint_id: str) -> bool:
        """
        Check if checkpoint exists (TODO-168 Day 3).

        Auto-detects compressed and uncompressed checkpoints.

        Args:
            checkpoint_id: ID of checkpoint

        Returns:
            True if checkpoint exists
        """
        compressed_path = self.base_dir / f"{checkpoint_id}.jsonl.gz"
        uncompressed_path = self.base_dir / f"{checkpoint_id}.jsonl"
        return compressed_path.exists() or uncompressed_path.exists()


# Export all public types
__all__ = [
    "StorageBackend",
    "FilesystemStorage",
]
