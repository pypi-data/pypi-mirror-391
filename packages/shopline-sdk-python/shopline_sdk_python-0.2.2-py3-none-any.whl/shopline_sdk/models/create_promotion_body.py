"""Shopline API 数据模型 - CreatePromotionBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .addon_product import AddonProduct
from .gift import Gift
from .money import Money
from .promotion import Promotion
from .promotion_condition import PromotionCondition
from .translatable import Translatable



class PromotionConfig(BaseModel):
    """Configuration model for promotion"""
    discount_on: Optional[Union[Literal['order', 'item', 'category'], str]] = None
    discount_type: Optional[Union[Literal['percentage', 'amount', 'gift', 'addon', 'free_shipping', 'bundle_pricing', 'bundle_group', 'member_point_redeem_gift', 'subscription_gift'], str]] = None
    title_translations: Optional[Translatable] = None
    discount_percentage: Optional[float] = None
    discount_amount: Optional[Money] = None
    conditions: Optional[List[Dict[str, Any]]] = None
    requires_membership: Optional[bool] = None
    whitelisted_membership_tier_ids: Optional[List[str]] = None
    whitelisted_tag_contents: Optional[List[str]] = None
    user_max_use_count: Optional[int] = None
    codes: Optional[List[str]] = None
    show_coupon: Optional[bool] = None
    max_use_count: Optional[int] = None
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    whitelisted_delivery_option_ids: Optional[List[str]] = None
    whitelisted_payment_ids: Optional[List[str]] = None
    discountable_product_ids: Optional[List[str]] = None
    discountable_category_ids: Optional[List[str]] = None
    discountable_quantity: Optional[int] = None
    for_affiliate_campaign: Optional[bool] = None
    is_accumulated: Optional[bool] = None
    first_purchase_only: Optional[bool] = None
    first_purchase_all_platform: Optional[bool] = None
    discounted_price: Optional[Money] = None
    status: Optional[Union[Literal['active', 'draft', 'hidden'], str]] = None
    available_platforms: Optional[List[str]] = None
    available_channel_ids: Optional[List[str]] = None
    coupon_type: Optional[Union[Literal['draw'], str]] = None
    benefit_tiers: Optional[List[Dict[str, Any]]] = None
    addon_products: Optional[List[Dict[str, Any]]] = None
    banner_media_ids: Optional[List[str]] = None
    term_translations: Optional[Translatable] = None
    gifts: Optional[List[Dict[str, Any]]] = None

class CreatePromotionBody(BaseModel):
    """Payload for creating promotion"""
    promotion: Optional[PromotionConfig] = None