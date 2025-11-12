"""Shopline API 数据模型 - Paginatable"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Paginatable(BaseModel):
    current_page: Optional[int] = None
    """The current page number 當前分頁"""
    per_page: Optional[int] = None
    """Number of result per page 每頁顯示 n 筆資料 (Default: 24)"""
    total_count: Optional[int] = None
    """Number of result in total 資料總量"""
    total_pages: Optional[int] = None
    """Number of pages in total 總頁數量"""