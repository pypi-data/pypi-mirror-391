"""Shopline API 数据模型 - ProductReviewComment"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class ProductReviewComment(BaseModel):
    id: Optional[str] = None
    """ID"""
    product_id: Optional[str] = None
    """Product ID"""
    order_id: Optional[str] = None
    """Order ID (if any)"""
    user_id: Optional[str] = None
    """Customer ID (if any)"""
    user_name: Optional[str] = None
    """Name of the reviewer (only applicable on imported review) 評論作者的名稱（只適用於導入評論）"""
    status: Optional[str] = None
    score: Optional[int] = None
    comment: Optional[str] = None
    """The content of the review comment"""
    media: Optional[Dict[str, Any]] = None
    """Object contains url of image in different dimensions 包含不同大小圖片的連絡"""
    created_by: Optional[str] = None
    commented_at: Optional[str] = None
    """Commented time 評論時間"""
    updated_at: Optional[str] = None
    """Updated time 更新時間"""
    created_at: Optional[str] = None
    """Created time 建立時間"""