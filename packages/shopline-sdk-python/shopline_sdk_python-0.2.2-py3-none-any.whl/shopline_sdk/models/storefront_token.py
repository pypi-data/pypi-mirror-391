"""Shopline API 数据模型 - StorefrontToken"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .storefront_token_merchant import StorefrontTokenMerchant


class StorefrontToken(BaseModel):
    """The merchant that this storefront token can access"""
    id: Optional[str] = None
    """Token ID 令牌ID"""
    token: Optional[str] = None
    """A JWT storefront token string JWT店面令牌字串"""
    staff_id: Optional[str] = None
    """ID of the staff that created this token 創建這令牌的staff ID"""
    application_id: Optional[str] = None
    """ID of the application that created this token 創建這令牌的程式"""
    merchant: Optional[StorefrontTokenMerchant] = None
    staff: Optional[StorefrontTokenMerchant] = None
    backend_token: Optional[bool] = None
    """Indicate if it is a backend token for different setup such as ratelimit"""
    created_at: Optional[str] = None
    """The date and time when the token was created 令牌創建的日期和時間"""