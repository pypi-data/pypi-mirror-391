"""Shopline API 数据模型 - ProductRevenues"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .paginatable import Paginatable
from .product_revenue import ProductRevenue


class ProductRevenues(BaseModel):
    items: Optional[List[ProductRevenue]] = None
    pagination: Optional[Paginatable] = None