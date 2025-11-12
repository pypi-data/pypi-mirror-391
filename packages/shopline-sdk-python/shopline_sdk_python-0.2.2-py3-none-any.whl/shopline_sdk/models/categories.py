"""Shopline API 数据模型 - Categories"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .category import Category
from .paginatable import Paginatable


class Categories(BaseModel):
    pagination: Optional[Paginatable] = None
    items: Optional[List[Category]] = None