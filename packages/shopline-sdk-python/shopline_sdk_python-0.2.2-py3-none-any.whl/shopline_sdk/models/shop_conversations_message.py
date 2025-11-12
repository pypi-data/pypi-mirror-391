"""Shopline API 数据模型 - ShopConversationsMessage"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class MessageConfig(BaseModel):
    """Configuration model for message"""
    sender_id: Optional[str] = None
    """Sender ID 發送者 ID"""
    sender_type: Optional[Union[Literal['User', 'Merchant', 'Bot'], str]] = None
    """Sender Type 發送者類型"""
    created_at: Optional[str] = None
    """Created At 訊息建立時間"""
    acting_sender_id: Optional[str] = None
    """Performer ID 發送者 ID"""
    is_sent_by_merchant: Optional[bool] = None
    """Is Sent by Merchant 是否為 merchant 發送訊息"""
    content: Optional[str] = None
    """Content 文字內容"""
    attachment: Optional[Dict[str, Any]] = None

class ShopConversationsMessage(BaseModel):
    id: Optional[str] = None
    """Message ID 訊息 ID"""
    platform: Optional[Union[Literal['shop_messages', 'order_messages'], str]] = None
    """Conversation Type 訊息種類"""
    message: Optional[MessageConfig] = None