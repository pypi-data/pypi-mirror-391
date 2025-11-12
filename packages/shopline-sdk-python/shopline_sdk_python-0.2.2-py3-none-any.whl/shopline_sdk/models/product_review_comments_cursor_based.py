"""Shopline API 数据模型 - ProductReviewCommentsCursorBased"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .cursor_based_paginatable import CursorBasedPaginatable
from .product_review_comment import ProductReviewComment


class ProductReviewCommentsCursorBased(BaseModel):
    last_id: Optional[str] = None
    limit: Optional[int] = None
    items: Optional[List[ProductReviewComment]] = None