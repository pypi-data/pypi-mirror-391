"""Shopline API 数据模型 - MembershipTier"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .member_point_rule import MemberPointRule
from .membership_tier_rule import MembershipTierRule
from .promotion import Promotion
from .translatable import Translatable
from .user_credit_rule import UserCreditRule


class MembershipTier(BaseModel):
    id: Optional[str] = None
    """Membership tier's ID 會員等級ID"""
    level: Optional[int] = None
    """Level of Current Membership Tier 等級高低 - *Having higher level with larger number. 等級數越高，數字越大"""
    name_translations: Optional[Translatable] = None
    member_count: Optional[int] = None
    """Number of members in this tier 此等級的會員人數"""
    membership_tier_rules: Optional[List[MembershipTierRule]] = None
    promotions: Optional[List[Promotion]] = None
    member_point_rules: Optional[List[MemberPointRule]] = None
    user_credit_rules: Optional[List[UserCreditRule]] = None