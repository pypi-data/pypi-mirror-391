"""Shopline API 数据模型 - OrderCampaignItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .translatable import Translatable


class OrderCampaignItem(BaseModel):
    id: Optional[str] = None
    """Order Campaign Item ID 訂單推薦活動ID"""
    name_translations: Optional[Translatable] = None
    type: Optional[Union[Literal['affiliate_referral', 'member_referral'], str]] = None
    """Campaign Type 推薦活動類型"""
    reward_type: Optional[Union[Literal['percentage', 'amount'], str]] = None
    """Campaign Reward Type 推薦活動獎勵類型"""
    reward_value: Optional[Money] = None
    campaign_data: Optional[Dict[str, Any]] = None
    """Campaign Data 推薦活動參數"""
    campaign_id: Optional[str] = None
    """Campaign ID 推薦活動ID"""
    order_id: Optional[str] = None
    """Order ID 訂單ID"""
    bonus_balance: Optional[Money] = None