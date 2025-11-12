"""Shopline API 数据模型 - UpdatePromotionBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .addon_product import AddonProduct
from .gift import Gift
from .promotion import Promotion
from .promotion_condition import PromotionCondition
from .translatable import Translatable



class ConditionsItem(BaseModel):
    """Item model for conditions"""
    id: Optional[str] = None
    min_item_count: Optional[int] = None
    min_price: Optional[float] = None
    whitelisted_product_ids: Optional[List[str]] = None
    whitelisted_category_ids: Optional[List[str]] = None
    blacklisted_product_ids: Optional[List[str]] = None


class Benefit_TiersItem(BaseModel):
    """Item model for benefit_tiers"""
    id: Optional[str] = None
    min_item_count: Optional[int] = None
    min_price: Optional[float] = None
    discountable_product_ids: Optional[str] = None


class Addon_ProductsItem(BaseModel):
    """Item model for addon_products"""
    addon_product_id: Optional[str] = None
    discounted_price: Optional[float] = None
    discountable_quantity: Optional[float] = None


class GiftsItem(BaseModel):
    """Item model for gifts"""
    gift_id: Optional[str] = None
    discounted_point: Optional[float] = None

class UpdatePromotionBody(BaseModel):
    """Payload for updating promotion"""
    title_translations: Optional[Translatable] = None
    discountable_product_ids: Optional[List[str]] = None
    discountable_category_ids: Optional[List[str]] = None
    is_accumulated: Optional[bool] = None
    requires_membership: Optional[bool] = None
    whitelisted_membership_tier_ids: Optional[List[str]] = None
    whitelisted_tag_contents: Optional[List[str]] = None
    user_max_use_count: Optional[int] = None
    conditions: Optional[List[ConditionsItem]] = None
    benefit_tiers: Optional[List[Benefit_TiersItem]] = None
    show_coupon: Optional[bool] = None
    max_use_count: Optional[int] = None
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    whitelisted_delivery_option_ids: Optional[List[str]] = None
    whitelisted_payment_ids: Optional[List[str]] = None
    banner_media_ids: Optional[List[str]] = None
    seo_enabled: Optional[bool] = None
    seo_title_translations: Optional[Translatable] = None
    seo_description_translations: Optional[Translatable] = None
    seo_keywords: Optional[str] = None
    term_translations: Optional[Translatable] = None
    addon_products: Optional[List[Addon_ProductsItem]] = None
    gifts: Optional[List[GiftsItem]] = None