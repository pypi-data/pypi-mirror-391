"""Shopline API 数据模型 - CreateReturnOrderBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .return_order import ReturnOrder
from .return_order_delivery_address import ReturnOrderDeliveryAddress



class Payment_OptionConfig(BaseModel):
    """Configuration model for payment_option"""
    id: Optional[str] = None
    """payment option id, required when return_by is not shop 支付信息ID"""
    key: Optional[str] = None
    """payment option key, required when return_by is shop 支付信息key"""


class Delivery_OptionConfig(BaseModel):
    """Configuration model for delivery_option"""
    id: Optional[str] = None
    """delivery option key 物流ID"""
    key: Optional[str] = None
    """delivery option id 物流key"""

class CreateReturnOrderBody(BaseModel):
    """Payload for creating return order"""
    order_id: str
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_phone_country_code: Optional[str] = None
    country: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    logistic_codes: Optional[List[str]] = None
    payment_option: Payment_OptionConfig
    """payment option 支付信息"""
    delivery_option: Delivery_OptionConfig
    """delivery option 物流信息"""
    subtotal_items: Any
    bank_account: Optional[Any] = None
    """bank account, available when payment option type is bank_transfer_return  銀行賬號，當payment option type是bank_transfer_return時可用"""
    returned_by: Optional[Any] = None