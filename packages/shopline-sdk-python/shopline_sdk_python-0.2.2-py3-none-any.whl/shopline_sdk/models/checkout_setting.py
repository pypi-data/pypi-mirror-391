"""Shopline API 数据模型 - CheckoutSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .category import Category
from .translatable import Translatable



class Rounding_SettingConfig(BaseModel):
    """Configuration model for rounding_setting"""
    enabled: Optional[bool] = None
    smallest_denomination: Optional[int] = None
    rounding_mode: Optional[str] = None


class Multi_CheckoutConfig(BaseModel):
    """Configuration model for multi_checkout"""
    enabled: Optional[bool] = None
    cart_tags: Optional[List[Dict[str, Any]]] = None

class CheckoutSetting(BaseModel):
    enable_fast_checkout_qty: Optional[bool] = None
    enable_tc_location_redesign: Optional[bool] = None
    enable_ec_fast_checkout: Optional[bool] = None
    enable_sc_fast_checkout: Optional[bool] = None
    checkout_without_customer_name: Optional[bool] = None
    enforce_user_login_on_checkout: Optional[bool] = None
    checkout_without_email: Optional[bool] = None
    enabled_abandoned_cart_notification: Optional[bool] = None
    enable_membership_autocheck: Optional[bool] = None
    enable_subscription_autocheck: Optional[bool] = None
    rounding_setting: Optional[Rounding_SettingConfig] = None
    multi_checkout: Optional[Multi_CheckoutConfig] = None