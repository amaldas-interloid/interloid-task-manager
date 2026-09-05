from app.exceptions.base import AppException


class TaskNotFoundException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Task not found",
            code="TASK_NOT_FOUND",
            status_code=404,
        )
