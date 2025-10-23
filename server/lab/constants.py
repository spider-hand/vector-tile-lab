from enum import Enum


class TaskStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


TASK_STATUS_CHOICES = [(status.value, status.name) for status in TaskStatus]


class ClassificationMethod(str, Enum):
    QUANTILE = "quantile"
    NATURAL_BREAKS = "natural_breaks"


CLASSIFICATION_METHOD_CHOICES = [
    (method.value, method.name) for method in ClassificationMethod
]
