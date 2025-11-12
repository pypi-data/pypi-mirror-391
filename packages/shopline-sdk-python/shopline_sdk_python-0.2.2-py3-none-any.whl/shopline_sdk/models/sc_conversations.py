"""Shopline API 数据模型 - SCConversations"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .paginatable import Paginatable
from .sc_conversation import SCConversation


class SCConversations(BaseModel):
    pagination: Optional[Paginatable] = None
    items: Optional[List[SCConversation]] = None