"""SwarmCoordinator - manages roles, task delegation, and swarm health."""

from typing import Dict, List, Optional, Tuple

from .agent import SwarmAgent
from .roles import ExplorerRole, WorkerRole, ValidatorRole
from .task import Task
from .types import TaskStatus


class SwarmCoordinator:
    """
    Coordinates a decentralized swarm of agents with smarter assignment.

    Features:
    - Capability & role-based filtering
    - Simple load balancing (least loaded agent first)
    - Proper task status updates
    """

    def __init__(self, swarm_id: str):
        self.swarm_id = swarm_id
        self.agents: Dict[str, SwarmAgent] = {}
        self.tasks: Dict[str, Task] = {}
        self._agent_load: Dict[str, int] = {}  # Track current task load per agent

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
        """
        Assign a task to the best available agent.

        Assignment strategy (in order):
        1. Must be able to handle the task type
        2. Prefer lower current load (load balancing)
        3. Update task status to ASSIGNED on success
        """
        task = self.tasks.get(task_id)
        if not task:
            print(f"[Coordinator] Task {task_id} not found.")
            return None

        # Find all capable agents
        capable_agents: List[Tuple[int, str, SwarmAgent]] = []

        for agent_id, agent in self.agents.items():
            if agent.can_handle_task(task):
                load = self._agent_load.get(agent_id, 0)
                capable_agents.append((load, agent_id, agent))

        if not capable_agents:
            print(f"[Coordinator] No agent can handle task '{task.description}' (type={task.task_type})")
            return None

        # Sort by load (ascending), then by agent_id for determinism
        capable_agents.sort(key=lambda x: (x[0], x[1]))

        # Assign to the least loaded capable agent
        best_load, best_agent_id, best_agent = capable_agents[0]

        if best_agent.assign_task(task):
            self._agent_load[best_agent_id] = best_load + 1
            task.status = TaskStatus.ASSIGNED          # <-- NEW
            print(f"[Coordinator] Assigned task '{task.description}' to {best_agent_id} (load={best_load + 1})")
            return best_agent_id

        print(f"[Coordinator] Failed to assign task to {best_agent_id}")
        return None

    def get_swarm_status(self) -> Dict:
        return {
            "swarm_id": self.swarm_id,
            "agent_count": len(self.agents),
            "active_tasks": len([t for t in self.tasks.values() if t.status != TaskStatus.COMPLETED]),
            "agent_loads": dict(self._agent_load),
        }
