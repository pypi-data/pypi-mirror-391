"""Shopline API 数据模型 - MembershipInfo"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .membership_tier_rule import MembershipTierRule
from .translatable import Translatable



class Membership_TierConfig(BaseModel):
    """Configuration model for membership_tier"""
    id: Optional[str] = Field(default=None, alias="_id")
    """Membership tier's ID 會員等級ID"""
    level: Optional[int] = None
    """Level of Current Membership Tier 等級高低"""
    name_translations: Optional[Translatable] = None
    merchant_id: Optional[str] = None
    """merchant ID"""
    exclusive_product_count: Optional[int] = None
    """Number of exlcusive products in this membership tier  這個會員級別不能購買的產品數目"""
    promotion_count: Optional[int] = None
    """Number of promotions in this membership tier  這個會員級別的優惠數目"""
    valid_period: Optional[Dict[str, Any]] = None
    """Valid period of this membership tier  這個會員級別的有效時段"""
    membership_tier_rules: Optional[List[MembershipTierRule]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Membership_Tier_GapConfig(BaseModel):
    """Configuration model for membership_tier_gap"""
    next_tier: Optional[Dict[str, Any]] = None
    """Membership Tier Data 顧客會員等級"""
    next_discount: Optional[float] = None
    """The discount of next membership tier<br />下一個會員等級的折扣優惠"""
    user_spending: Optional[float] = None
    """The amount used to determine if a member meets the upgrade criteria, based on the "Membership Upgrade Condition" in the SHOPLINE Admin:  - For "Single Purchase," returns the highest order amount that meets the threshold   during the membership period, or 0 if none meet the threshold.  - For "Purchase within specified period," returns the total spending within that period.  Returns null if the member is already at the highest tier.    用於判斷會員是否符合升級條件的消費金額，依據 Admin 中的「會員升級條件」設定決定回傳值：  - 若條件為「單次購物」，檢查目前會籍期間內是否有任一筆訂單達到門檻。若有訂單達門檻，則回傳金額最高者；若皆未達門檻，回傳 0。  - 若條件為「指定期限內購物」，回傳在指定期限內的累積消費金額。  若會員已達最高等級，則回傳 null。"""
    user_spendings_for_extend: Optional[float] = None
    """The amount used to determine if a member meets the extend criteria, based on the "Membership extension condition" in the SHOPLINE Admin:  - For "Single Purchase," returns the highest order amount that meets the threshold   during the membership period, or 0 if none meet the threshold.  - For "Purchase within specified period," returns the total spending within that period.  Returns null if the current membership has a permanent duration.    用於判斷會員是否符合續會條件的消費金額，依據 Admin 中的「會員續會條件」設定決定回傳值：  - 若條件為「單次購物」，檢查目前會籍期間內是否有任一筆訂單達到門檻。若有訂單達門檻，則回傳金額最高者；若皆未達門檻，回傳 0。  - 若條件為「指定期限內購物」，回傳在指定期限內的累積消費金額。  若當前會籍為永久期限，則回傳 null。"""
    next_total_spending: Optional[float] = None
    """The amount of upgrading to next membership tier.<br /> 升等到下一會員等級所需之消費金額（Admin 設定的升級金額條件）  *若沒有下一級則回傳 null"""
    extend_total_spending: Optional[float] = None
    """The amount of extending in current membership tier.<br /> 續會目前會員等級所需之消費金額（Admin 設定的續會金額條件）  *若沒有設定則回傳 null"""

class MembershipInfo(BaseModel):
    id: Optional[str] = None
    """Membership tier's ID 會員等級ID"""
    membership_tier: Optional[Membership_TierConfig] = None
    """Membership Tier Data 顧客會員等級"""
    tier_expires_at: Optional[str] = None
    """The Membership Tier Expiry Time 會員到期時間"""
    membership_tier_gap: Optional[Membership_Tier_GapConfig] = None
    """Next membership tier's info 下一個會員等級的資料"""