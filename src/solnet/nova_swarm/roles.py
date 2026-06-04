"""Role definitions for decentralized swarm agents."""

from enum import Enum

from .types import RoleType


class Role:
    """Base class for swarm agent roles."""

    def __init__(self, role_type: RoleType):
        self.role_type = role_type

    def can_handle(self, task_type: str) -> bool:
        """Return whether this role can handle a given task type."""
        return True  # Default: accept all (override in subclasses)


class ExplorerRole(Role):
    """Explorer role - discovers tasks, resources, or opportunities."""

    def __init__(self):
        super().__init__(RoleType.EXPLORER)

    def can_handle(self, task_type: str) -> bool:
        return task_type in ["discovery", "exploration", "monitoring"]


class WorkerRole(Role):
    """Worker role - executes assigned tasks."""

    def __init__(self):
        super().__init__(RoleType.WORKER)

    def can_handle(self, task_type: str) -> bool:
        return task_type in ["execution", "computation", "action"]


class ValidatorRole(Role):
    """Validator role - verifies results and maintains swarm quality."""

    def __init__(self):
        super().__init__(RoleType.VALIDATOR)

    def can_handle(self, task_type: str) -> bool:
        return task_type in ["validation", "review", "consensus"]
