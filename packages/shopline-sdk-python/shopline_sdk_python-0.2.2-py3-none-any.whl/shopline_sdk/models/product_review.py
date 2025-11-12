"""Shopline API 数据模型 - ProductReview"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class RatingConfig(BaseModel):
    """Configuration model for rating"""
    one: Optional[int] = None
    two: Optional[int] = None
    three: Optional[int] = None
    four: Optional[int] = None
    five: Optional[int] = None

class ProductReview(BaseModel):
    id: Optional[str] = None
    """ID"""
    product_id: Optional[str] = None
    """Product ID"""
    avg_score: Optional[float] = None
    """Review score in average 評論平均分數"""
    total_comments_count: Optional[int] = None
    """Number of comments in total 評論總數"""
    imported_comments_count: Optional[int] = None
    """Number of comments imported 已導入評論總數"""
    rating: Optional[RatingConfig] = None