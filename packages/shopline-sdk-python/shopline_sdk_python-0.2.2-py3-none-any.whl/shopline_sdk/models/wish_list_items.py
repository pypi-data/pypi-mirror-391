"""Shopline API 数据模型 - WishListItems"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .cursor_based_paginatable import CursorBasedPaginatable
from .wish_list_item import WishListItem


class WishListItems(BaseModel):
    last_id: Optional[str] = None
    limit: Optional[int] = None
    items: Optional[List[WishListItem]] = None