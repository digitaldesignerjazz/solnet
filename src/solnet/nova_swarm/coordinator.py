"""SwarmCoordinator - manages roles, task delegation, and swarm health."""

from typing import Dict, List, Optional

from .agent import SwarmAgent
from .roles import ExplorerRole, WorkerRole, ValidatorRole
from .task import Task


class SwarmCoordinator:
    """
    Coordinates a decentralized swarm of agents.

    Responsible for role assignment, task distribution,
    and maintaining overall swarm health and emergent behavior.
    """

    def __init__(self, swarm_id: str):
        self.swarm_id = swarm_id
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: Dict[str, Task] = {}

    def register_agent(self, agent: SwarmAgent):
        self.agents[agent.agent_id] = agent

    def create_task(self, description: str, task_type: str = "general", priority: int = 1) -> Task:
        task = Task(
            task_id=f"task-{len(self.tasks)+1}",
            description=description,
            task_type=task_type,
            priority=priority,
        )
        self.tasks[task.task_id] = task
        return task

    def assign_task(self, task_id: str) -> Optional[str]:
        task = self.tasks.get(task_id)
        if not task:
            return None

        for agent in self.agents.values():
            if agent.can_handle_task(task):
                if agent.assign_task(task):
                    return agent.agent_id
        return None

    def get_swarm_status(self) -> Dict:
        return {
            "swarm_id": self.swarm_id,
            "agent_count": len(self.agents),
            "active_tasks": len([t for t in self.tasks.values() if t.status.name == "PENDING"]),
        }
