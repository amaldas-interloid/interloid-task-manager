from enum import StrEnum


class TaskStatus(StrEnum):
    TODO = "Todo"
    IN_PROGRESS = "In Progress"
    DONE = "Done"


class TaskPriority(StrEnum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"