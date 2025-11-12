"""Shopline API 数据模型 - Channels"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .channel import Channel
from .paginatable import Paginatable


class Channels(BaseModel):
    pagination: Optional[Paginatable] = None
    items: Optional[List[Channel]] = None