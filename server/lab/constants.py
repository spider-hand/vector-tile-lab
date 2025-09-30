from enum import Enum


class TaskStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


TASK_STATUS_CHOICES = [(status.value, status.name) for status in TaskStatus]
