"""Shopline API 数据模型 - UserCoupon"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class UserCoupon(BaseModel):
    id: Optional[str] = None
    """User Coupon ID"""
    user_id: Optional[str] = None
    """User ID 使用者 ID"""