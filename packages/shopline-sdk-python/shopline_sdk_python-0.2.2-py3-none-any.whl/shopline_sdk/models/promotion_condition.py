"""Shopline API 数据模型 - PromotionCondition"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money


class PromotionCondition(BaseModel):
    id: Optional[str] = None
    """Promotion Condition ID 優惠活動條件ID"""
    min_item_count: Optional[int] = None
    """滿件數量"""
    min_price: Optional[Money] = None
    """滿額"""
    type: Optional[Union[Literal['red', 'green'], str]] = None
    """A組(紅標)或B組(綠標) -  Applicable when discount_type is bundle_group"""
    whitelisted_product_ids: Optional[List[str]] = None
    """指定商品條件id"""
    whitelisted_category_ids: Optional[List[str]] = None
    """指定分類條件id"""
    blacklisted_product_ids: Optional[List[str]] = None
    """指定排除商品條件id"""
    subscription_period: Optional[int] = None
    """subscription period 定期購指定期數"""