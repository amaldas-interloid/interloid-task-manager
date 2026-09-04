from app.exceptions.base import AppException


class EmailAlreadyExistsException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Email already exists",
            code="EMAIL_ALREADY_EXISTS",
            status_code=409,
        )


class InvalidCredentialsException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Invalid email or password",
            code="INVALID_CREDENTIALS",
            status_code=401,
            details=None,
        )


class InvalidRefreshTokenException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Invalid or expired refresh token",
            code="INVALID_REFRESH_TOKEN",
            status_code=401,
            details=None,
        )


class UnauthorizedException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Invalid or missing authentication credentials",
            code="UNAUTHORIZED",
            status_code=401,
            details=None,
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )


class InvalidCurrentPasswordException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Current Password is incorrect",
            code="INVALID_CURRENT_PASSWORD",
            status_code=401,
            details=None,
        )


class ForbiddenException(AppException):
    def __init__(
        self,
        message: str = "you do not have the permission to perform this action",
        code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=403,
            details=None,
        )
