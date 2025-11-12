"""Shopline API 数据模型 - UserCoupons"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .paginatable import Paginatable
from .user_coupon import UserCoupon


class UserCoupons(BaseModel):
    pagination: Optional[Paginatable] = None
    items: Optional[List[UserCoupon]] = None