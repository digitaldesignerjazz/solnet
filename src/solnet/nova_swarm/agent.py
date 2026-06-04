"""SwarmAgent base class for NovaSwarm."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .roles import Role
from .task import Task
from .types import AgentState, SwarmMessage


@dataclass
class SwarmAgent:
    """
    Base class for agents participating in a NovaSwarm.

    Agents have roles, can handle tasks, maintain emotional state,
    and communicate via SolNet (Hyperspace + Yggdrasil).
    """

    agent_id: str
    role: Role
    state: AgentState
    capabilities: List[str] = field(default_factory=list)
    current_tasks: int = 0  # Simple local load tracking

    def can_handle_task(self, task: Task) -> bool:
        """Check if this agent can handle the given task."""
        return self.role.can_handle(task.task_type)

    def assign_task(self, task: Task) -> bool:
        if self.can_handle_task(task):
            task.assigned_to = self.agent_id
            self.current_tasks += 1
            return True
        return False

    def send_message(self, message: SwarmMessage) -> bool:
        """Send a message to another agent or broadcast (via SolNet)."""
        # TODO(issue-1): Integrate with SwarmCommunication / HyperspaceTunnel
        print(f"[{self.agent_id}] Sending message: {message.message_type}")
        return True

    def receive_message(self, message: SwarmMessage):
        """Handle incoming message."""
        # TODO(issue-1): Process incoming swarm messages
        print(f"[{self.agent_id}] Received: {message.message_type}")

    def update_emotional_state(self, updates: Dict[str, float]):
        """Update emotional/loyalty state (inspired by Circuit 1.0)."""
        self.state.emotional_state.update(updates)
