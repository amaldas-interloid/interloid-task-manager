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
        )


class InvalidRefreshTokenException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Invalid or expired refresh token",
            code="INVALID_REFRESH_TOKEN",
            status_code=401,
        )


class UnauthorizedException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Invalid or missing authentication credentials",
            code="UNAUTHORIZED",
            status_code=401,
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )


class InvalidCurrentPasswordException(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Current password is incorrect",
            code="INVALID_CURRENT_PASSWORD",
            status_code=401,
        )


class ForbiddenException(AppException):
    def __init__(
        self,
        message: str = "You do not have permission to perform this action",
        code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
            status_code=403,
        )
