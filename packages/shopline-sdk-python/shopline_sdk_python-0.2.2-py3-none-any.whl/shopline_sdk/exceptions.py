"""
Shopline SDK 异常类
"""

from typing import Any, Optional
from pydantic import BaseModel


class ShoplineAPIError(Exception):
    """Shopline API 错误异常"""
    
    def __init__(
        self, 
        code: str = None, 
        message: str = None, 
        status_code: int = 500,
        error: Optional[BaseModel] = None,
        **extra
    ):
        """
        初始化 Shopline API 错误
        
        Args:
            code: 错误代码
            message: 错误消息
            status_code: HTTP 状态码
            error: 错误响应模型实例
            **kwargs: 其他错误数据
        """
        self.code = code or getattr(error, "code", None)
        self.message = message or getattr(error, "message", None) or getattr(error, "error", None)
        self.status_code = status_code
        self.error = error
        self.extra = extra
        
        super().__init__(f"[{code}] {message}")
    
    def __str__(self) -> str:
        return f"ShoplineAPIError({self.status_code}): [{self.code}] {self.message}"
    
    def __repr__(self) -> str:
        return (
            f"ShoplineAPIError(code='{self.code}', message='{self.message}', "
            f"status_code={self.status_code}, extra={self.extra})"
        )
