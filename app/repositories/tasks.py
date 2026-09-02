from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums.task import TaskPriority, TaskStatus
from app.models.task import Task


class TaskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.flush()
        await self.session.refresh(task)
        return task

    async def get_tasks(
        self,
        *,
        owner_id: UUID | None = None,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        due_from: date | None,
        due_to: date | None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Task], int]:
        filters = []

        if owner_id is not None:
            filters.append(Task.owner_id == owner_id)

        if status is not None:
            filters.append(Task.status == status)

        if priority is not None:
            filters.append(Task.priority == priority)

        if due_from is not None:
            filters.append(Task.due_date >= due_from)

        if due_to is not None:
            filters.append(Task.due_date <= due_to)

        if search:
            filters.append(Task.title.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(Task).where(*filters)

        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()

        stmt = (
            select(Task)
            .where(*filters)
            .order_by(Task.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(stmt)

        tasks = list(result.scalars().all())

        return tasks, total

    async def get_by_id(
        self,
        id: UUID,
    ) -> Task | None:
        stmt = select(Task).where(
            Task.id == id,
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def update(
        self,
        task: Task,
    ) -> Task:
        await self.session.flush()
        await self.session.refresh(task)

        return task

    async def delete(
        self,
        task: Task,
    ) -> None:
        await self.session.delete(task)
        await self.session.flush()
