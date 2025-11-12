"""Shopline API 数据模型 - OrderDeliveryAddress"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class OrderDeliveryAddress(BaseModel):
    country_code: Optional[str] = None
    """Country Code 國家代碼"""
    country: Optional[str] = None
    """Country 國家"""
    city: Optional[str] = None
    """City 城市"""
    district: Optional[str] = None
    """City 地區"""
    state: Optional[str] = None
    """Stage or Region 州/省/地區"""
    postcode: Optional[str] = None
    """ZIP code 郵政編號"""
    address_1: Optional[str] = None
    """Address 1 地址 1"""
    address_2: Optional[str] = None
    """Address 1 地址 2 (這裡原則上會自動帶入地址所在行政區)"""
    key: Optional[str] = None
    layer1: Optional[str] = None
    layer2: Optional[str] = None
    layer3: Optional[str] = None
    logistic_codes: Optional[List[str]] = None
    recipient_name: Optional[str] = None
    """Recipient Name 收件人姓名"""
    recipient_phone: Optional[str] = None
    """Recipient Phone 收件人電話號碼"""
    recipient_phone_country_code: Optional[str] = None
    """Recipient Phone Country Code 收件人電話號碼國碼"""
    remarks: Optional[str] = None
    """Remark 備註"""