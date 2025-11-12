"""Shopline API 数据模型 - SCConversationsMessages"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .sc_conversations_message import SCConversationsMessage


class SCConversationsMessages(BaseModel):
    total: Optional[int] = None
    """Total Number 總筆數"""
    limit: Optional[int] = None
    """Numbers of Shop Messages 顯示筆數"""
    items: Optional[List[SCConversationsMessage]] = None