"""
全局异常处理与错误响应模块
提供统一的异常类型和错误响应格式
"""
from fastapi import HTTPException, status
from typing import Any, Dict, Optional, List


class AppException(HTTPException):
    """应用基础异常类"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None
    ):
        self.error_code = error_code or f"ERR_{status_code}"
        self.errors = errors
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ResourceNotFoundException(AppException):
    """资源未找到异常"""
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_type} with id {resource_id} not found",
            error_code="RESOURCE_NOT_FOUND"
        )


class PermissionDeniedException(AppException):
    """权限不足异常"""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PERMISSION_DENIED"
        )


class InvalidOperationException(AppException):
    """无效操作异常"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_OPERATION"
        )


class ValidationErrorException(AppException):
    """数据验证错误异常"""
    def __init__(self, errors: List[Dict[str, Any]]):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Validation error",
            error_code="VALIDATION_ERROR",
            errors=errors
        )


class DatabaseErrorException(AppException):
    """数据库错误异常"""
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR"
        )