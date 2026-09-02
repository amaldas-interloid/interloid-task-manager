from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.enums.task import TaskPriority, TaskStatus


class TaskCreateRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None


class TaskUpdateRequest(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=200,
    )
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None


class TaskResponse(BaseModel):
    id: UUID
    owner_id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListQuery(BaseModel):
    owner_id: UUID | None = None

    status: TaskStatus | None = None
    priority: TaskPriority | None = None

    due_from: date | None = None
    due_to: date | None = None

    search: str | None = None

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )

    offset: int = Field(
        default=0,
        ge=0,
    )

    @model_validator(mode="after")
    def validate_due_date_range(self) -> "TaskListQuery":
        if (
            self.due_from is not None
            and self.due_to is not None
            and self.due_from > self.due_to
        ):
            raise ValueError("due_from must be less than or equal to due_to")

        return self


class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    pagination: PaginationMeta
