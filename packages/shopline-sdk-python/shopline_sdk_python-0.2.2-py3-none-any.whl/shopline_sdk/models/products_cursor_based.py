"""Shopline API 数据模型 - ProductsCursorBased"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .cursor_based_paginatable import CursorBasedPaginatable
from .product import Product


class ProductsCursorBased(BaseModel):
    last_id: Optional[str] = None
    limit: Optional[int] = None
    items: Optional[List[Product]] = None
    removed_item_ids: Optional[List[Any]] = None
    price_sets: Optional[Dict[str, Any]] = None