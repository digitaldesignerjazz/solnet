"""NovaSwarm - Decentralized, privacy-preserving swarm intelligence layer for SolNet.

This module provides the foundation for emotional, self-improving, and decentralized
multi-agent swarms running over SolNet's mesh + hyperspace networking.
"""

from .agent import SwarmAgent

from .coordinator import SwarmCoordinator
from .roles import Role, ExplorerRole, WorkerRole, ValidatorRole
from .task import Task, TaskStatus
from .communication import SwarmCommunication
from .types import SwarmMessage, AgentState

__all__ = [
    "SwarmAgent",
    "SwarmCoordinator",
    "Role",
    "ExplorerRole",
    "WorkerRole",
    "ValidatorRole",
    "Task",
    "TaskStatus",
    "SwarmCommunication",
    "SwarmMessage",
    "AgentState",
]
