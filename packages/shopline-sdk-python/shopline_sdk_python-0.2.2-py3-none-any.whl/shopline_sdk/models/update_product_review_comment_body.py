"""Shopline API 数据模型 - UpdateProductReviewCommentBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .product_review_comment import ProductReviewComment


class UpdateProductReviewCommentBody(BaseModel):
    """Payload for updating product review comment"""
    user_name: Optional[str] = None
    status: Optional[str] = None
    score: Optional[int] = None
    comment: Optional[str] = None
    media_ids: Optional[List[str]] = None
    """Array of media ids 媒體id陣列"""