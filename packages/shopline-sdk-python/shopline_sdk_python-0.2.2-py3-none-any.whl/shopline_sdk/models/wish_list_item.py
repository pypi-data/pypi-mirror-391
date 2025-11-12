"""Shopline API 数据模型 - WishListItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .product import Product
from .product_variation import ProductVariation
from .translatable import Translatable



class ProductConfig(BaseModel):
    """Configuration model for product"""
    id: Optional[str] = None
    title_translations: Optional[Translatable] = None
    field_titles: Optional[List[Dict[str, Any]]] = None
    price: Optional[Money] = None
    price_sale: Optional[Money] = None
    hide_price: Optional[bool] = None
    same_price: Optional[bool] = None
    lowest_price: Optional[Money] = None
    max_order_quantity: Optional[int] = None
    status: Optional[Union[Literal['active', 'draft', 'removed', 'hidden'], str]] = None
    sku: Optional[str] = None
    flash_price_sets: Optional[List[Dict[str, Any]]] = None
    member_price: Optional[Money] = None
    unlimited_quantity: Optional[bool] = None
    quantity: Optional[float] = None
    available_start_time: Optional[str] = None
    available_end_time: Optional[str] = None
    variation: Optional[ProductVariation] = None

class WishListItem(BaseModel):
    id: Optional[str] = None
    """Wish list item ID."""
    product: Optional[ProductConfig] = None
    variation_key: Optional[str] = None
    """Variation key. Variation 的 key   If this wish list item is not a variation, the variation_key will be an empty string.  如果此 item 是一般商品不是規格，則 variation_key 會是空字串"""