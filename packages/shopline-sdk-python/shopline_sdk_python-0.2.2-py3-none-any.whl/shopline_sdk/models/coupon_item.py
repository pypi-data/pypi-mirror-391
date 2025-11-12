"""Shopline API 数据模型 - CouponItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .translatable import Translatable



class Coupon_ItemConfig(BaseModel):
    """Configuration model for coupon_item"""
    coupon_code: Optional[str] = None
    """Coupon Code 酷碰券代碼"""
    discounted_amount: Optional[Money] = None
    """Discount Amount 折扣金額"""

class CouponItem(BaseModel):
    id: Optional[str] = None
    """優惠 ID"""
    cart_tag_id: Optional[str] = None
    """Cart Tag ID 購物車溫層 ID"""
    coupon_item: Optional[Coupon_ItemConfig] = None
    discounted_amount: Optional[Money] = None
    """Discount Amount 折抵固定金額（優惠類型為 固定金額 時）"""
    discount_on: Optional[str] = None
    """Discount On 優惠生效等級"""
    discount_percentage: Optional[float] = None
    """Discount Percentage 折抵百分比數（優惠類型為 %折扣 時）"""
    discount_type: Optional[str] = None
    """Discount Type 優惠類型"""
    discounted_price: Optional[Money] = None
    """Discounted Price 加購品優惠折抵金額"""
    extended_promotion_id: Optional[str] = None
    """Extended Promotion ID 多階層優惠所對應的主要優惠活動 ID"""
    is_accumulated: Optional[bool] = None
    """Is Accumulated Promotion 是否是自動累計優惠"""
    is_extend_promotion: Optional[bool] = None
    """Is Extend Promotion 是否是多階層優惠"""
    is_membership_tier_promotion: Optional[bool] = None
    """Is Membership Tier Promotion 是否是會員分級專屬優惠"""
    membership_tier_id: Optional[str] = None
    """Membership Tier ID 會員分級專屬優惠 ID"""
    requires_membership: Optional[bool] = None
    """Requires Membership 需要會員資格"""
    summary_translations: Optional[Translatable] = None
    """Summary Translations 優惠簡介"""
    title_translations: Optional[Translatable] = None
    """Title Translations 優惠標題"""
    whitelisted_membership_tier_ids: Optional[List[str]] = None
    """Whitelisted Membership Tier IDs 可使用的會員等級 IDs"""