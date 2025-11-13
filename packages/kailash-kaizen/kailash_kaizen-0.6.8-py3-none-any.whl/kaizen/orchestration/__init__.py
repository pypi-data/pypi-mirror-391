"""
Kaizen Orchestration - Multi-Agent Coordination and Pipelines

This module provides orchestration patterns for coordinating multiple agents
and creating composable pipelines.

Submodules:
- patterns: Multi-agent coordination patterns (SupervisorWorker, Consensus, etc.)
- core: Core orchestration infrastructure (patterns, teams)
- pipeline: Pipeline infrastructure for composability
"""

# Explicit exports from core modules
from kaizen.orchestration import core, patterns  # noqa: F401
from kaizen.orchestration.pipeline import Pipeline, SequentialPipeline

__all__ = [
    # Core modules
    "patterns",
    "core",
    # Pipeline infrastructure
    "Pipeline",
    "SequentialPipeline",
]
