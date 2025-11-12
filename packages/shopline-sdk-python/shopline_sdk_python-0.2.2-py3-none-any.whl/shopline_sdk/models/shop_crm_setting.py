"""Shopline API 数据模型 - ShopCrmSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Referral_ProductConfig(BaseModel):
    """Configuration model for referral_product"""
    enabled: Optional[bool] = None
    referral_hours: Optional[float] = None

class ShopCrmSetting(BaseModel):
    enable_switch_channel: Optional[bool] = None
    enable_staff_send_sms_and_signup: Optional[bool] = None
    enable_maintain_customer_profile: Optional[bool] = None
    enable_enter_spend_amount: Optional[bool] = None
    enable_customer_overview: Optional[bool] = None
    enable_agent_performance: Optional[bool] = None
    enable_channel_performance: Optional[bool] = None
    enable_edit_customer_tags: Optional[bool] = None
    enable_edit_customer_memo: Optional[bool] = None
    referral_product: Optional[Referral_ProductConfig] = None