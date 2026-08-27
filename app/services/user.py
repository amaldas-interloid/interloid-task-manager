from uuid import UUID

from app.exceptions.user import (
    SelfModificationNotAllowedException,
    UserNotFoundException,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import UserResponse
from app.schemas.user import UserListResponse, UserUpdateRequest


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    async def list_users(
            self,
            limit: int,
            offset: int,
    ) -> UserListResponse:
        users, total = await self.user_repository.list_users(
            limit=limit,
            offset=offset,
        )

        items = [
            UserResponse(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at,
            )
            for user in users
        ]

        return UserListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def update_user(
            self,
            id: UUID,
            request: UserUpdateRequest,
            current_admin: User,
    ) -> UserResponse:
        user = await self.user_repository.get_by_id(id)

        if user is None:
            raise UserNotFoundException()

        if user.id == current_admin.id:
            if request.role is not None and request.role != current_admin.role:
                raise SelfModificationNotAllowedException()

            if request.is_active is not None and request.is_active is False:
                raise SelfModificationNotAllowedException()
            
        user = await self.user_repository.update_user(
            user=user,
            role=request.role,
            is_active=request.is_active,
        )

        return UserResponse(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
        )