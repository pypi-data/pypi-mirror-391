"""Shopline API 数据模型 - MembershipTierRule"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Condition_IntervalConfig(BaseModel):
    """Configuration model for condition_interval"""
    type: Optional[Union[Literal['within_interval', 'single_purchase'], str]] = None
    """Membership Upgrade Condition Type<br /> 會員升級條件類別<br /> - within_interval: 指定期限內購物<br /> - single_purchase: 單次購物"""
    time_unit: Optional[Union[Literal['month'], str]] = None
    """Membership Upgrade Condition Time Unit<br /> 會員升級條件時間單位"""
    time_value: Optional[int] = None
    """Valid Period of the conditional interval if the type is "within_interval"<br /> 如類別是"within_interval"，升級條件時間的值"""


class Effect_IntervalConfig(BaseModel):
    """Configuration model for effect_interval"""
    type: Optional[Union[Literal['within_interval', 'unlimited'], str]] = None
    """Membership Valid Period<br /> 會員有效期限"""
    time_unit: Optional[Union[Literal['month'], str]] = None
    """Unit of Valid Period<br /> 有效期限單位"""
    time_value: Optional[int] = None
    """Valid Period of the effect interval if the type is "within_interval"<br /> 如類別是"within_interval"，有效期間的值"""


class Total_SpendingConfig(BaseModel):
    """Configuration model for total_spending"""
    cents: Optional[int] = None
    """Total Spending Requirement represent in cents<br /> 以仙為單位表示總消費要求"""
    currency_symbol: Optional[str] = None
    """Total Spending Requirement represent in currency_symbol<br /> 以currency_symbol表示總消費要求"""
    currency_iso: Optional[str] = None
    """Total Spending Requirement represent in currency_iso<br /> 以currency_iso表示總消費要求"""
    label: Optional[str] = None
    """Total Spending Requirement represent in label<br /> 以標籤表示總消費要求"""
    dollars: Optional[float] = None
    """Total Spending Requirement represent in dollars<br /> 以元為單位表示總消費要求"""

class MembershipTierRule(BaseModel):
    id: Optional[str] = None
    """Membership tier rule's ID<br />會員等級規則ID"""
    effect_type: Optional[Union[Literal['upgrade', 'extend'], str]] = None
    """Type of the membership_tier_rule<br /> 會員級別規則的類別"""
    condition_interval: Optional[Condition_IntervalConfig] = None
    effect_interval: Optional[Effect_IntervalConfig] = None
    total_spending: Optional[Total_SpendingConfig] = None
    created_at: Optional[str] = None
    """The timestamp that the rule is created at<br />規則創造時間"""
    updated_at: Optional[str] = None
    """The timestamp that the rule is updated at<br />規則更新時間"""