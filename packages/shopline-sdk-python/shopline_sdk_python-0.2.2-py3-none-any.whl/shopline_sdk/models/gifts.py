"""Shopline API 数据模型 - Gifts"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .gift import Gift
from .paginatable import Paginatable


class Gifts(BaseModel):
    pagination: Optional[Paginatable] = None
    items: Optional[List[Gift]] = None