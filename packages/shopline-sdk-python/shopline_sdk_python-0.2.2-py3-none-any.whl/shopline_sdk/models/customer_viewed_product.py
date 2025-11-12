"""Shopline API 数据模型 - CustomerViewedProduct"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class CustomerViewedProduct(BaseModel):
    product_id: Optional[str] = None
    """Product's ID 商品 ID"""
    view_count: Optional[int] = None
    """Product's View Count 商品瀏覽次數"""
    last_visited_at: Optional[str] = None
    """Product's Last Visited At 商品最後瀏覽時間"""