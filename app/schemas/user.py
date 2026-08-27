from pydantic import BaseModel

from app.enums.role import RoleName
from app.schemas.auth import UserResponse


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int
    limit: int
    offset: int

class UserUpdateRequest(BaseModel):
    role: RoleName | None = None
    is_active: bool | None = None