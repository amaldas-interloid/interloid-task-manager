from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.task import TaskCreateRequest, TaskResponse
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
        error= None,
    )

    

    
