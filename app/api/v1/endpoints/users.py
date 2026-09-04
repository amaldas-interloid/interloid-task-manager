from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.api.responses import (
    FORBIDDEN_RESPONSE,
    NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.db.dependencies import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import UserResponse
from app.schemas.common import APIResponse
from app.schemas.user import UserListResponse, UserUpdateRequest
from app.services.user import UserService

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    response_model=APIResponse[UserListResponse],
    status_code=status.HTTP_200_OK,
    responses={
        **UNAUTHORIZED_RESPONSE,
        **FORBIDDEN_RESPONSE,
        **VALIDATION_ERROR_RESPONSE,
    },
)
async def list_users(
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    _: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> APIResponse[UserListResponse]:
    repository = UserRepository(session)
    service = UserService(repository)

    users = await service.list_users(
        limit=limit,
        offset=offset,
    )

    return APIResponse(
        success=True,
        message="users retrieved successfully",
        data=users,
    )


@router.patch(
    "/{id}",
    response_model=APIResponse[UserResponse],
    status_code=status.HTTP_200_OK,
    responses={
        **UNAUTHORIZED_RESPONSE,
        **FORBIDDEN_RESPONSE,
        **NOT_FOUND_RESPONSE,
        **VALIDATION_ERROR_RESPONSE,
    },
)
async def update_user(
    id: UUID,
    request: UserUpdateRequest,
    current_admin: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> APIResponse[UserResponse]:
    repository = UserRepository(session)
    service = UserService(repository)

    user = await service.update_user(
        id=id,
        request=request,
        current_admin=current_admin,
    )

    return APIResponse(
        success=True,
        message="User updated successfully",
        data=user,
    )
