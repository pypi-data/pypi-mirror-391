"""Shopline API 数据模型 - ProductReviews"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .paginatable import Paginatable
from .product_review import ProductReview


class ProductReviews(BaseModel):
    items: Optional[List[ProductReview]] = None
    pagination: Optional[Paginatable] = None