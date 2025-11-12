"""Shopline API 数据模型 - CreateProductReviewCommentBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .product_review_comment import ProductReviewComment


class CreateProductReviewCommentBody(BaseModel):
    """Payload for creating product review comment"""
    product_id: Optional[str] = None
    score: Optional[int] = None
    comment: Optional[str] = None
    user_id: Optional[str] = None
    order_id: Optional[str] = None
    status: Optional[str] = None
    user_name: Optional[str] = None
    media_ids: Optional[List[str]] = None
    """Array of media ids 媒體id陣列"""