from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.repositories.tasks import TaskRepository
from app.schemas.task import TaskCreateRequest, TaskResponse


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.task_repository = TaskRepository(session)

    async def create_task(
            self,
            request: TaskCreateRequest,
            owner_id,
    ) -> TaskResponse:
        task = Task(
            owner_id=owner_id,
            title=request.title,
            description=request.description,
            status=request.status,
            priority=request.priority,
            due_date=request.due_date,
        )

        task = await self.task_repository.create(task)

        return TaskResponse.model_validate(task)