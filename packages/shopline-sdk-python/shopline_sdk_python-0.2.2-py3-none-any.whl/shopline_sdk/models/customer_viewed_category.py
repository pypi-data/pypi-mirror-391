"""Shopline API 数据模型 - CustomerViewedCategory"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class CustomerViewedCategory(BaseModel):
    category_id: Optional[str] = None
    """Category's ID 分類 ID"""
    view_count: Optional[int] = None
    """Category's View Count 分類瀏覽次數"""
    last_visited_at: Optional[str] = None
    """Category's Last Visited At 分類最後瀏覽時間"""