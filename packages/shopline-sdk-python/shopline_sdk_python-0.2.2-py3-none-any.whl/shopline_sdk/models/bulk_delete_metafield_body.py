"""Shopline API 数据模型 - BulkDeleteMetafieldBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .metafield_value import MetafieldValue


class BulkDeleteMetafieldBody(BaseModel):
    """Payload for updating metafield"""
    id: Optional[str] = None
    namespace: Optional[str] = None
    key: Optional[str] = None