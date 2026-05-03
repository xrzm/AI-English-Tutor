from __future__ import annotations

from typing import Generic, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: str = "ok"

    @classmethod
    def success_response(cls, data: T, message: str = "ok") -> "ApiResponse[T]":
        return cls(success=True, data=data, message=message)


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
