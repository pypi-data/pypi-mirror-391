"""Shopline API 数据模型 - OrderDeliveryData"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class OrderDeliveryData(BaseModel):
    hk_sfplus_home_region: Optional[str] = None
    location_code: Optional[str] = None
    """Store Code 便利商店店號"""
    location_name: Optional[str] = None
    """Store Code 便利商店店號"""
    name_translations: Optional[Translatable] = None
    store_address: Optional[str] = None
    """Store Address 商店地址"""
    url: Optional[str] = None
    """Delivery Tracking url 貨件追蹤URL"""
    tracking_number: Optional[str] = None
    """Delivery Tracking Number 貨件追蹤號碼"""
    scheduled_delivery_date: Optional[str] = None
    """Scheduled Delivery Date 預計貨到時間"""
    time_slot_key: Optional[str] = None
    """Scheduled Delivery Time Slot 送貨時段 ---  If delivery platform istcat 當送貨方式是黑貓時  1 = before 13:00 / 13:00 前 2 = 14:00 - 18:00  4 = any time slot / 任何時間"""
    time_slot_translations: Optional[Translatable] = None