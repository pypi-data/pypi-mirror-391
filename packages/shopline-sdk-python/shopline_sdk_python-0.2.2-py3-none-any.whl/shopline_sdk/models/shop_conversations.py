"""Shopline API 数据模型 - ShopConversations"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .paginatable import Paginatable
from .shop_conversation import ShopConversation


class ShopConversations(BaseModel):
    pagination: Optional[Paginatable] = None
    items: Optional[List[ShopConversation]] = None