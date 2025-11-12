"""Shopline API 数据模型 - UserCreditRule"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Apply_ConditionsItem(BaseModel):
    """Item model for apply_conditions"""
    credit_value: Optional[int] = None
    """Credit Value 購物金"""
    apply_threshold: Optional[int] = None
    """Apply Threshold 購物金折抵門檻"""

class UserCreditRule(BaseModel):
    id: Optional[str] = None
    status: Optional[Union[Literal['active', 'inactive'], str]] = None
    rule_type: Optional[Union[Literal['pos_apply_credit', 'auto_reward', 'apply_partial_credit', 'welcome_credit', 'birthday_credit', 'max_amount_per_order', 'max_percentage_per_order', 'apply_user_credit'], str]] = None
    """pos_apply_credit: POS 購物金折抵 auto_reward: 滿額送購物金 apply_partial_credit: 允許顧客自行設定折抵金額 welcome_credit: 新加入會員購物金 birthday_credit: 生日購物金 max_amount_per_order: (舊) 購物金折抵上限 by amount max_percentage_per_order: (舊) 購物金折抵上限 by percentage apply_user_credit: (新) 折抵購物金上限，支援多層級設定"""
    credit_value: Optional[int] = None
    """購物金"""
    credit_value_type: Optional[Union[Literal['amount', 'percentage'], str]] = None
    """Only the rule whose rule_type is apply_user_credit will use this field to distinguish the credit_value is fixed amount or percentage.  僅 rule_type 為 apply_user_credit 的規則會使用到，用來區分 credit_value 的值是固定金額還是百分比"""
    credit_valid_period: Optional[int] = None
    """購物金有效日期（天），0 / -1 代表無限"""
    credit_threshold: Optional[int] = None
    """購物金生效條件"""
    is_accumulated: Optional[bool] = None
    """自動累計"""
    accumulated_type: Optional[Union[Literal['credit', 'percentage'], str]] = None
    """累計類型 credit: 固定金額 percentage: 百分比"""
    apply_threshold: Optional[int] = None
    """購物金生效條件"""
    apply_conditions: Optional[List[Apply_ConditionsItem]] = None
    """Tiered application of user credits. 套用購物金折抵條件(多階層)"""
    created_at: Optional[str] = None
    """Created Date 創造時間 (UTC +0)"""
    updated_at: Optional[str] = None
    """Created Date 更新時間 (UTC +0)"""