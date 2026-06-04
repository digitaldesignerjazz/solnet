"""Shared types and enums for NovaSwarm."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, Optional


class RoleType(Enum):
    EXPLORER = auto()
    WORKER = auto()
    VALIDATOR = auto()
    COORDINATOR = auto()


class TaskStatus(Enum):
    PENDING = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class SwarmMessage:
    """Message passed between swarm agents."""
    sender_id: str
    receiver_id: Optional[str] = None  # None = broadcast
    message_type: str = "general"
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: __import__("time").time())


@dataclass
class AgentState:
    """Current state of a swarm agent."""
    agent_id: str
    role: RoleType
    status: str = "active"
    capabilities: list[str] = field(default_factory=list)
    emotional_state: Dict[str, float] = field(default_factory=dict)  # e.g. loyalty, energy
    last_update: float = field(default_factory=lambda: __import__("time").time())
