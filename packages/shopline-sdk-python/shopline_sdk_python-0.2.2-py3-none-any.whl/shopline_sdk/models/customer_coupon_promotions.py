"""Shopline API 数据模型 - CustomerCouponPromotions"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .customer_promotion import CustomerPromotion


class CustomerCouponPromotions(BaseModel):
    promotion_id: Optional[CustomerPromotion] = Field(default=None, alias="{promotion_id}")