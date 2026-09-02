from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    details: Any | None = None


class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T | None = None
    error: ErrorDetail | None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    data: None = None
    error: ErrorDetail
