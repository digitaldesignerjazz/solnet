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
class PersonalityTraits:
    """Defines an agent's personality, influencing emotional dynamics."""
    energy_baseline: float = 0.8      # Natural energy level
    fatigue_rate: float = 0.15        # How fast fatigue increases per task
    recovery_rate: float = 0.08       # How fast energy recovers over time
    loyalty: float = 0.7              # Tendency to stay committed to tasks/swarm


@dataclass
class AgentState:
    """Current state of a swarm agent, including emotional and personality data."""
    agent_id: str
    role: 'RoleType'
    status: str = "active"
    capabilities: list[str] = field(default_factory=list)

    # Emotional state (0.0 - 1.0)
    energy: float = 0.8
    fatigue: float = 0.0

    # Personality (influences emotional dynamics)
    personality: PersonalityTraits = field(default_factory=PersonalityTraits)

    last_update: float = field(default_factory=lambda: __import__("time").time())


@dataclass
class SwarmMessage:
    """Message passed between swarm agents."""
    sender_id: str
    receiver_id: Optional[str] = None
    message_type: str = "general"
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=lambda: __import__("time").time())
