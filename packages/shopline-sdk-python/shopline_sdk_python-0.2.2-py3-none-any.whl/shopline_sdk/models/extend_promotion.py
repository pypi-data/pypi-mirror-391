"""Shopline API 数据模型 - ExtendPromotion"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .promotion_condition import PromotionCondition


class ExtendPromotion(BaseModel):
    id: Optional[str] = None
    """Promotion ID 優惠活動ID"""
    discount_percentage: Optional[float] = None
    """Discount percentage 折扣百分比 - *Applicable when discount_type is percentage 當discount_type為percentage時適用"""
    discount_amount: Optional[Money] = None
    discountable_quantity: Optional[int] = None
    """Quantity 獲得數量 - *When discount_type is gift, this field refers to quantity of gift 當discount_type為gift時，此為贈品數量  *When discount_type is addon, this field refers to quality of add-on 當discount_type為addon時，此為可加購數量"""
    discounted_point: Optional[int] = None
    """Amount of point to redeem gift 點數兌換 - *Applicable when discount_type is member_point_redeem_gift 當discount_type為member_point_redeem_gift時適用"""
    discounted_price: Optional[Money] = None
    discountable_product_ids: Optional[List[str]] = None
    """Ids of Discounted product 指定商品ids"""
    conditions: Optional[List[PromotionCondition]] = None