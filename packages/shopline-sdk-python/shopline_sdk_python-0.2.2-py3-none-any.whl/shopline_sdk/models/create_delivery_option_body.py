"""Shopline API 数据模型 - CreateDeliveryOptionBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .delivery_option import DeliveryOption
from .money import Money
from .translatable import Translatable



class Config_DataConfig(BaseModel):
    """Configuration model for config_data"""
    lead_time: Optional[Dict[str, Any]] = None
    max_lead_time: Optional[Dict[str, Any]] = None
    excluded_weekdays: Optional[Dict[str, Any]] = None
    excluded_dates: Optional[Dict[str, Any]] = None
    delivery_time_required: Optional[Dict[str, Any]] = None
    specific_delivery_time_translations: Optional[Dict[str, Any]] = None
    delivery_target_area: Optional[Dict[str, Any]] = None

class CreateDeliveryOptionBody(BaseModel):
    """Payload for creating delivery option"""
    status: Optional[Union[Literal['active', 'draft'], str]] = None
    name_translations: Translatable
    description_translations: Optional[Translatable] = None
    show_description_on_checkout: Optional[bool] = None
    delivery_time_description_translations: Optional[Translatable] = None
    config_data: Optional[Config_DataConfig] = None
    requires_customer_address: Optional[bool] = None
    fee_type: Union[Literal['flat', 'flat_weight', 'subtotal', 'item_count', 'sl_logistic'], str]
    delivery_rates: List[Dict[str, Any]]
    region_type: Optional[Union[Literal['custom'], str]] = None
    """Delivery Option Code 送貨方式代碼  Only support creating "custom" region_type through open api"""
    delivery_type: Optional[Union[Literal['custom'], str]] = None
    """Only support creating "custom" delivery_type through open api"""