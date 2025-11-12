"""Shopline API 数据模型 - status"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class status(BaseModel):
    """The status that will be applied on the products to the online store.  更新商品狀態至網店。"""
    value: Literal['active', 'draft']
    """Enum values: active, draft"""