"""Shopline API 数据模型 - CategoryLayout"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .link import Link
from .translatable import Translatable


class CategoryLayout(BaseModel):
    id: Optional[str] = None
    """Category ID 分類ID"""
    name_translations: Optional[Translatable] = None
    description_translations: Optional[Translatable] = None
    key: Optional[str] = None
    """Special category 特殊分類鍵"""
    count: Optional[int] = None
    """Product count 分類商品數量"""
    link: Optional[Link] = None
    children: Optional[List[Dict[str, Any]]] = None
    """Array of Sub Categories Information 子分類資訊序列"""