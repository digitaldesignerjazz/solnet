"""SwarmCoordinator with emotional + loyalty-aware assignment and collaboration tracking."""

from typing import Dict, List, Optional, Tuple

import time

from .agent import SwarmAgent
from .roles import ExplorerRole, WorkerRole, ValidatorRole
from .task import Task
from .types import TaskStatus


class SwarmCoordinator:
    """
    Coordinates a decentralized swarm with emotional state and loyalty dynamics.

    Supports loyalty from successful collaboration and loyalty decay.
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

                # Loyalty bonus from already assigned agents
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

    def complete_task(self, task_id: str):
        """Mark a task as completed and boost loyalty between involved agents."""
        task = self.tasks.get(task_id)
        if not task or not task.assigned_to:
            return

        task.status = TaskStatus.COMPLETED
        assigned_agent_id = task.assigned_to

        # Boost loyalty between the assigned agent and others who contributed
        # (Simple version: boost with all other active agents)
        for other_id, other_agent in self.agents.items():
            if other_id != assigned_agent_id and self._agent_load.get(other_id, 0) > 0:
                self.agents[assigned_agent_id].record_successful_collaboration(other_id, boost=0.08)
                other_agent.record_successful_collaboration(assigned_agent_id, boost=0.08)

        print(f"[Coordinator] Task '{task.description}' completed. Loyalty boosted.")

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
