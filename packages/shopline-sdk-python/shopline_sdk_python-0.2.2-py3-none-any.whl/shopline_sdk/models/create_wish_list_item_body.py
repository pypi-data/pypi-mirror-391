"""Shopline API 数据模型 - CreateWishListItemBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Product_Set_DatasItem(BaseModel):
    """Item model for product_set_datas"""
    child_product_id: Optional[str] = None
    """Child product ID 子商品ID"""
    child_variation_id: Optional[str] = None
    """Child product's variation key 子商品規格key"""
    quantity: Optional[float] = None
    """Child product quantity 子商品數量"""

class CreateWishListItemBody(BaseModel):
    """Payload for creating wish list item"""
    customer_id: str
    """Customer ID 顧客 ID"""
    product_id: str
    """Product ID 商品ID"""
    variation_key: str
    """Product's variation's key 商品規格key  If product does not have variations, please set to empty string. 若商品無規格，請填入空字串"""
    product_set_datas: Optional[List[Product_Set_DatasItem]] = None
    """Product set information 組合商品資訊"""