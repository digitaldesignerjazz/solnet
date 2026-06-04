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

    Supports emotional state, personality traits, fatigue, loyalty, and dynamic relationship evolution.
    """

    agent_id: str
    role: Role
    state: AgentState
    capabilities: List[str] = field(default_factory=list)
    current_tasks: int = 0
    comm: Optional[SwarmCommunication] = None

    def can_handle_task(self, task: Task) -> bool:
        return self.role.can_handle(task.task_type)

    def assign_task(self, task: Task) -> bool:
        if self.can_handle_task(task):
            task.assigned_to = self.agent_id
            self.current_tasks += 1
            self._apply_fatigue_from_task()
            return True
        return False

    def _apply_fatigue_from_task(self):
        p = self.state.personality
        fatigue_increase = p.fatigue_rate
        self.state.fatigue = min(1.0, self.state.fatigue + fatigue_increase)
        self.state.energy = max(0.0, self.state.energy - fatigue_increase * 0.5)

    def update_emotional_state(self, updates: Dict[str, float]):
        for key, value in updates.items():
            if hasattr(self.state, key):
                current = getattr(self.state, key)
                setattr(self.state, key, max(0.0, min(1.0, current + value)))

    def decay_emotions(self, time_delta: float = 1.0):
        p = self.state.personality

        if self.state.energy < p.energy_baseline:
            recovery = p.recovery_rate * time_delta
            self.state.energy = min(p.energy_baseline, self.state.energy + recovery)

        decay = 0.05 * time_delta
        self.state.fatigue = max(0.0, self.state.fatigue - decay)

        self.state.last_update = time.time()

    # === Loyalty System ===

    def update_loyalty(self, other_agent_id: str, delta: float):
        current = self.state.loyalty_map.get(other_agent_id, 0.5)
        new_value = max(0.0, min(1.0, current + delta))
        self.state.loyalty_map[other_agent_id] = new_value

    def get_loyalty_toward(self, other_agent_id: str) -> float:
        return self.state.loyalty_map.get(other_agent_id, 0.5)

    def decay_loyalty(self, time_delta: float = 1.0, decay_rate: float = 0.02):
        """Loyalty toward other agents slowly decays over time if not reinforced."""
        for other_id in list(self.state.loyalty_map.keys()):
            current = self.state.loyalty_map[other_id]
            new_value = max(0.0, current - (decay_rate * time_delta))
            self.state.loyalty_map[other_id] = new_value

    def record_successful_collaboration(self, other_agent_id: str, boost: float = 0.1):
        """Increase loyalty after successful joint work."""
        self.update_loyalty(other_agent_id, boost)

    async def send_message(self, message: SwarmMessage) -> bool:
        if self.comm:
            return await self.comm.send_swarm_message(message)
        print(f"[{self.agent_id}] Sending message: {message.message_type}")
        return True

    def receive_message(self, message: SwarmMessage):
        print(f"[{self.agent_id}] Received: {message.message_type} from {message.sender_id}")
