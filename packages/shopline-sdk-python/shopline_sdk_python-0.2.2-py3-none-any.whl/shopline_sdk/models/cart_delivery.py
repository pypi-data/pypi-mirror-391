"""Shopline API 数据模型 - CartDelivery"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class CartDelivery(BaseModel):
    cart_tag_id: Optional[str] = None
    """Cart Tag ID 多購物車溫層 ID"""
    country: Optional[str] = None
    """Country 國家"""
    delivery_address: Optional[Dict[str, Any]] = None
    """Delivery Address 送貨地址"""
    delivery_data: Optional[Dict[str, Any]] = None
    """Delivery Data 送貨資訊"""
    delivery_option_id: Optional[str] = None
    """Delivery Option ID 送貨方式 ID"""
    postcode: Optional[str] = None
    """PostCode 郵遞區號"""
    region_code: Optional[str] = None
    """Region Code 地區"""
    payment_id: Optional[str] = None
    """Payment ID 付款方式 ID"""