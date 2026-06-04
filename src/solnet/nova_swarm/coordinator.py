"""SwarmCoordinator with full emotional and loyalty feedback loop."""

from typing import Dict, List, Optional, Tuple

import time

from .agent import SwarmAgent
from .roles import ExplorerRole, WorkerRole, ValidatorRole
from .task import Task
from .types import TaskStatus


class SwarmCoordinator:
    """
    Full emotional + loyalty-aware swarm coordinator with task outcome feedback.
    """

    def __init__(self, swarm_id: str):
        self.swarm_id = swarm_id
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self._agent_load: Dict[str, int] = {}

    def register_agent(self, agent: SwarmAgent):
        self.agents[agent.agent_id] = agent
        if agent.agent_id not in self._agent_load:
            self._agent_load[agent.agent_id] = 0

    def create_task(self, description: str, task_type: str = "general", priority: int = 1) -> Task:
        task = Task(
            task_id=f"task-{len(self.tasks) + 1}",
            description=description,
            task_type=task_type,
            priority=priority,
        )
        self.tasks[task.task_id] = task
        return task

    def assign_task(self, task_id: str) -> Optional[str]:
        task = self.tasks.get(task_id)
        if not task:
            print(f"[Coordinator] Task {task_id} not found.")
            return None

        capable_agents: List[Tuple[float, str, SwarmAgent]] = []

        for agent_id, agent in self.agents.items():
            if agent.can_handle_task(task):
                load = self._agent_load.get(agent_id, 0)
                fatigue_penalty = agent.state.fatigue * 3.0

                loyalty_bonus = 0.0
                for assigned_id in self._agent_load:
                    if self._agent_load[assigned_id] > 0:
                        loyalty = agent.get_loyalty_toward(assigned_id)
                        loyalty_bonus -= (1.0 - loyalty) * 0.5

                effective_load = load + fatigue_penalty + loyalty_bonus
                capable_agents.append((effective_load, agent_id, agent))

        if not capable_agents:
            print(f"[Coordinator] No capable agent for task: {task.description}")
            return None

        capable_agents.sort(key=lambda x: x[0])

        best_effective_load, best_agent_id, best_agent = capable_agents[0]

        if best_agent.assign_task(task):
            self._agent_load[best_agent_id] += 1
            task.status = TaskStatus.ASSIGNED
            print(f"[Coordinator] Assigned '{task.description}' to {best_agent_id}")
            return best_agent_id

        return None

    def complete_task(self, task_id: str, success: bool = True):
        """Mark task complete and apply emotional + loyalty feedback."""
        task = self.tasks.get(task_id)
        if not task or not task.assigned_to:
            return

        assigned_agent = self.agents.get(task.assigned_to)
        if not assigned_agent:
            return

        # Update task status
        task.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED

        # Apply emotional feedback to the assigned agent
        assigned_agent.on_task_completed(success=success)

        # Boost loyalty between collaborating agents
        for other_id, other_agent in self.agents.items():
            if other_id != task.assigned_to and self._agent_load.get(other_id, 0) > 0:
                assigned_agent.record_successful_collaboration(other_id, boost=0.06)
                other_agent.record_successful_collaboration(task.assigned_to, boost=0.06)

        status_text = "successfully" if success else "unsuccessfully"
        print(f"[Coordinator] Task '{task.description}' completed {status_text}. "
              f"Emotional feedback applied to {task.assigned_to}.")

    def decay_all_emotions(self, time_delta: float = 1.0):
        for agent in self.agents.values():
            agent.decay_emotions(time_delta)
            agent.decay_loyalty(time_delta)

    def get_swarm_status(self) -> Dict:
        return {
            "swarm_id": self.swarm_id,
            "agent_count": len(self.agents),
            "agent_loads": dict(self._agent_load),
            "average_fatigue": sum(a.state.fatigue for a in self.agents.values()) / max(1, len(self.agents)),
        }
