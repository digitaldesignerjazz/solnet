"""Task and Intent models for NovaSwarm."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .types import TaskStatus


@dataclass
class Task:
    """Represents a unit of work in the swarm."""
    task_id: str
    description: str
    task_type: str = "general"
    priority: int = 1
    payload: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    assigned_to: Optional[str] = None
    created_at: float = field(default_factory=lambda: __import__("time").time())
    completed_at: Optional[float] = None

    def mark_completed(self):
        self.status = TaskStatus.COMPLETED
        self.completed_at = __import__("time").time()

    def mark_failed(self):
        self.status = TaskStatus.FAILED
