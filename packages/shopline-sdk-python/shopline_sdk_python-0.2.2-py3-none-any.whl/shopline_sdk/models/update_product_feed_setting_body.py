"""Shopline API 数据模型 - UpdateProductFeedSettingBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class UpdateProductFeedSettingBody(BaseModel):
    """Payload for updating an product feed setting"""
    unique_ids: Optional[bool] = None
    """是否要用系統 id 取代 sku"""
    title: Optional[str] = None
    """The title of the product feed setting"""
    total_product_count: Optional[float] = None
    """The total product count of the product feed setting"""
    with_out_of_stock_product: Optional[bool] = None
    """Whether to include out of stock products"""
    with_preorder_product: Optional[bool] = None
    """Whether to include preorder products"""
    category_ids: Optional[List[str]] = None
    """The category ids of the product feed setting"""
    main_product_image_select: Optional[float] = None
    """The main product image select of the product feed setting"""
    variant_product_image_select: Optional[float] = None
    """The variant product image select of the product feed setting"""
    locale: Optional[str] = None
    """The locale of the product feed setting"""