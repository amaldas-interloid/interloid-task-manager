from app.exceptions.base import AppException


class UserNotFoundException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="User not Found",
            code="USER NOT FOUND",
            status_code=404,
            details=None,
        )


class SelfModificationNotAllowedException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Admins cannot deactivate or demote themselves",
            code="SELF_MODIFICATION_NOT_ALLOWED",
            status_code=422,
            details=None,
        )