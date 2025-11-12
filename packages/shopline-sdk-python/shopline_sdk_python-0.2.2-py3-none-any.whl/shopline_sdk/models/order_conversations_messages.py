"""Shopline API 数据模型 - OrderConversationsMessages"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .order_conversations_message import OrderConversationsMessage


class OrderConversationsMessages(BaseModel):
    total: Optional[int] = None
    """Total Number 總筆數"""
    limit: Optional[int] = None
    """Numbers of Order Messages 顯示筆數"""
    items: Optional[List[OrderConversationsMessage]] = None