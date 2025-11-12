"""Shopline API 数据模型 - UpdateProductVariationBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .product import Product


class UpdateProductVariationBody(BaseModel):
    """Payload for updating product variation"""
    location_id: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    """Price (Note: Cannot be set to null. Product with a price of 0 cannot be sold.)  原價格 (備註：不能設定為null。價格為0的商品不能被售出)"""
    retail_price: Optional[float] = None
    """Retail Price 零售價"""
    product_price_tiers: Optional[Dict[str, str]] = None
    """Membership tier's ID 會員等級ID"""
    member_price: Optional[float] = None
    """Member Price 會員價"""
    quantity: Optional[int] = None
    """Product Variation Quantity 規格商品數量 -  Directly update the quantity of the variation. The quantity is between -9999999 to 9999999.  直接更新規格商品數量。商品數量要在 -9999999 - 9999999 之間。"""
    preorder_limit: Optional[int] = None
    image: Optional[str] = None
    """Link of Images 圖片連結"""
    price_sale: Optional[float] = None
    """Price on sale  (Note: Cannot be set to null.   Product with a price_sale of 0 will be sold at its original price.)  特價 (備註：不能設定為null。特價為0的商品會以原價售出)"""
    cost: Optional[float] = None
    """Cost (Note: Cannot be set to null)  成本 (備註：不能設定為null)"""
    weight: Optional[float] = None
    """Weight (kg) 重量 (公斤)"""
    gtin: Optional[str] = None