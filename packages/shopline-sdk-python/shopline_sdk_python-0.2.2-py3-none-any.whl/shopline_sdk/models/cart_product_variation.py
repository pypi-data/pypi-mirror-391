"""Shopline API 数据模型 - CartProductVariation"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .translatable import Translatable


class CartProductVariation(BaseModel):
    id: Optional[str] = None
    """Product Variation ID 商品規格 ID"""
    fields_translations: Optional[Translatable] = None
    """Product Name 規格名稱"""
    price: Optional[Money] = None
    """Price 商品原價格"""
    out_of_stock_orderable: Optional[float] = None
    """Product's Current total orderable quantity 商品目前可購買總數量 -  *If unlimited_quantity is true or out_of_stock_orderable is true  this field will return -1"""
    fields: Optional[List[Dict[str, Any]]] = None
    """Fields"""
    max_order_quantity: Optional[float] = None
    """set maximum quantity per purchase for this product  商品單次購買上限  *-1 represents there's no quantity limit for each purchase  -1代表無商品單次購買的上限"""
    unlimited_quantity: Optional[bool] = None
    """Unlimited product quantity or not 商品數量是否無限"""
    quantity: Optional[float] = None
    """Quantity 商品數量"""
    total_orderable_quantity: Optional[float] = None
    """Product's Current total orderable quantity 商品目前可購買總數量 -  *If unlimited_quantity is true or out_of_stock_orderable is true  this field will return -1"""
    media: Optional[Dict[str, Any]] = None
    """Product Cover 規格圖片"""
    member_price: Optional[Money] = None
    """Member Price 會員價"""
    price_sale: Optional[Money] = None
    """Price on sale 特價"""