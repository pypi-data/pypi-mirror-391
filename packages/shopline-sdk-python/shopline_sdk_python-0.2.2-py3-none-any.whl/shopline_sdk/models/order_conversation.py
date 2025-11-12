"""Shopline API 数据模型 - OrderConversation"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Last_MessageConfig(BaseModel):
    """Configuration model for last_message"""
    id: Optional[str] = None
    """Conversation ID 對話 ID"""
    sender_id: Optional[Any] = None
    """Sender ID 留言發送方 ID"""
    sender_type: Optional[Any] = None
    """Sender Type 留言發送方"""
    created_at: Optional[str] = None
    """Created At 建立時間"""
    value: Optional[str] = None
    """Content 對話內容"""
    type: Optional[Union[Literal['text', 'image'], str]] = None
    """Conversation Type 對話類別"""

class OrderConversation(BaseModel):
    id: Optional[str] = None
    """Conversation ID 訊息 ID"""
    type: Optional[Union[Literal['shop_messages', 'order_messages'], str]] = None
    """Conversation Type 訊息平台"""
    customer_id: Optional[str] = None
    """Customer ID 客戶 ID"""
    order_number: Optional[str] = None
    """Order Number 訂單號碼"""
    system_order_number: Optional[str] = None
    """系统生成的訂單號 system order number"""
    merchant_order_number: Optional[str] = None
    """店家自定義訂單號 (會根據rollout_key選擇用哪個order_number)"""
    order_id: Optional[str] = None
    """Order ID 訂單ID"""
    last_message: Optional[Last_MessageConfig] = None