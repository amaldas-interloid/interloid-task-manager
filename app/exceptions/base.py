class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int,
        details: object | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details

        super().__init__(message)
