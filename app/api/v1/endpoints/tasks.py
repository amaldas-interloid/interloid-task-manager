from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_task_list_query
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.task import (
    TaskCreateRequest,
    TaskListQuery,
    TaskListResponse,
    TaskResponse,
    TaskUpdateRequest,
)
from app.services.task import TaskService

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.post(
    "",
    response_model=APIResponse[TaskResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    request: TaskCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TaskResponse]:
    service = TaskService(db)

    task = await service.create_task(
        request=request,
        owner_id=current_user.id,
    )

    return APIResponse(
        success=True,
        message="Task created successfully",
        data=task,
        error=None,
    )


@router.get(
    "",
    response_model=APIResponse[TaskListResponse],
    status_code=status.HTTP_200_OK,
)
async def get_tasks(
    query: Annotated[
        TaskListQuery,
        Depends(get_task_list_query),
    ],
    current_user: Annotated[
        User,
        Depends(get_current_user),
    ],
    db: Annotated[
        AsyncSession,
        Depends(get_db),
    ],
) -> APIResponse[TaskListResponse]:
    service = TaskService(db)

    result = await service.get_tasks(
        current_user=current_user,
        query=query,
    )

    return APIResponse(
        success=True,
        message="Tasks fetched successfully",
        data=result,
        error=None,
    )


@router.get(
    "/{id}",
    response_model=APIResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
)
async def get_task_by_id(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TaskResponse]:
    service = TaskService(db)

    task = await service.get_task_by_id(
        id=id,
        current_user=current_user,
    )

    return APIResponse(
        success=True,
        message="Task fetched successfully",
        data=task,
        error=None,
    )


@router.patch(
    "/{id}",
    response_model=APIResponse[TaskResponse],
    status_code=status.HTTP_200_OK,
)
async def update_task(
    id: UUID,
    request: TaskUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[TaskResponse]:
    service = TaskService(db)

    task = await service.update_task(
        id=id,
        current_user=current_user,
        request=request,
    )

    return APIResponse(
        success=True,
        message="Task updated successfully",
        data=task,
        error=None,
    )


@router.delete(
    "/{id}",
    response_model=APIResponse[None],
    status_code=status.HTTP_200_OK,
)
async def delete_task(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> APIResponse[None]:
    service = TaskService(db)

    await service.delete_task(
        id=id,
        current_user=current_user,
    )

    return APIResponse(
        success=True,
        message="Task deleted successfully",
        data=None,
        error=None,
    )
