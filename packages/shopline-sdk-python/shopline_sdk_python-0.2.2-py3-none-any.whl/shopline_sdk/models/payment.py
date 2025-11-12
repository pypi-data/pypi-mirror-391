"""Shopline API 数据模型 - Payment"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .payment_config_data import PaymentConfigData
from .translatable import Translatable


class Payment(BaseModel):
    id: Optional[str] = None
    """Payment Method ID 付款方式ID"""
    status: Optional[Union[Literal['active', 'draft'], str]] = None
    """Payment Method Status 付款方式狀態 - Status allows: active 啟用中  draft 隱藏"""
    fee_percent: Optional[float] = None
    """Percentage of Payment Fee 附加費之百分比"""
    fee_multiplier: Optional[float] = None
    """Multiplier of Payment Fee 附加費之乘數 - 假設附加費設定為10%，則 fee_percent=10%  fee_multiplier=0.1"""
    instructions_translations: Optional[Translatable] = None
    name_translations: Optional[Translatable] = None
    config_data: Optional[PaymentConfigData] = None
    type: Optional[str] = None
    """Payment's Type 付款方式代碼"""
    excluded_delivery_option_ids: Optional[List[str]] = None
    """Excluded Delivery Option ID 該付款方式排除的送貨方式ID"""
    binding_delivery_options: Optional[List[str]] = None
    """Binding delivery options codes 與該付款方式綁定的送貨方式代碼"""
    is_sl_payment_available: Optional[bool] = None
    """Whether the payment is available or not 付款方式是否可用"""
    show_description_on_checkout: Optional[bool] = None
    """Whether to display the payment description on checkout page 是否在結帳頁面顯示付款指示"""