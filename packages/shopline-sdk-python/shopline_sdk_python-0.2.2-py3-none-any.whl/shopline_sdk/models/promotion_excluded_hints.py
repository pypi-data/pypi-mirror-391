"""Shopline API 数据模型 - PromotionExcludedHints"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class PromotionExcludedHints(BaseModel):
    has_order_promotion_excluded_hint: Optional[bool] = None
    """Order Promotion Excluded Hint 排除全店優惠提示"""
    has_member_promotion_excluded_hint: Optional[bool] = None
    """Member Promotion Excluded Hint 排除會員優惠提示"""
    has_user_credit_excluded_hint: Optional[bool] = None
    """User Credit Excluded Hint 排除購物金折扣提示"""
    has_member_point_excluded_hint: Optional[bool] = None
    """Member Point Excluded Hint 排除會員點數折扣提示"""