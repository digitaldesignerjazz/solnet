"""SwarmAgent base class for NovaSwarm."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import time

from .communication import SwarmCommunication

from .roles import Role
from .task import Task
from .types import AgentState, PersonalityTraits, SwarmMessage


@dataclass
class SwarmAgent:
    """
    Base class for agents participating in a NovaSwarm.

    Supports emotional state, personality traits, and fatigue dynamics.
    """

    agent_id: str
    role: Role
    state: AgentState
    capabilities: List[str] = field(default_factory=list)
    current_tasks: int = 0
    comm: Optional[SwarmCommunication] = None

    def __post_init__(self):
        if not hasattr(self.state, 'personality') or self.state.personality is None:
            self.state.personality = PersonalityTraits()

    def can_handle_task(self, task: Task) -> bool:
        return self.role.can_handle(task.task_type)

    def assign_task(self, task: Task) -> bool:
        if self.can_handle_task(task):
            task.assigned_to = self.agent_id
            self.current_tasks += 1
            # Increase fatigue when taking a new task
            self._apply_fatigue_from_task()
            return True
        return False

    def _apply_fatigue_from_task(self):
        """Apply fatigue increase based on personality."""
        p = self.state.personality
        fatigue_increase = p.fatigue_rate
        self.state.fatigue = min(1.0, self.state.fatigue + fatigue_increase)
        self.state.energy = max(0.0, self.state.energy - fatigue_increase * 0.5)

    def update_emotional_state(self, updates: Dict[str, float]):
        """Manually update emotional state (e.g. from external events)."""
        for key, value in updates.items():
            if hasattr(self.state, key):
                current = getattr(self.state, key)
                setattr(self.state, key, max(0.0, min(1.0, current + value)))

    def decay_emotions(self, time_delta: float = 1.0):
        """
        Apply natural emotional decay / recovery over time.
        Called periodically by the coordinator or simulation loop.
        """
        p = self.state.personality

        # Energy recovers toward baseline
        if self.state.energy < p.energy_baseline:
            recovery = p.recovery_rate * time_delta
            self.state.energy = min(p.energy_baseline, self.state.energy + recovery)

        # Fatigue naturally decays
        decay = 0.05 * time_delta
        self.state.fatigue = max(0.0, self.state.fatigue - decay)

        self.state.last_update = time.time()

    async def send_message(self, message: SwarmMessage) -> bool:
        if self.comm:
            return await self.comm.send_swarm_message(message)
        print(f"[{self.agent_id}] Sending message: {message.message_type}")
        return True

    def receive_message(self, message: SwarmMessage):
        print(f"[{self.agent_id}] Received: {message.message_type} from {message.sender_id}")
