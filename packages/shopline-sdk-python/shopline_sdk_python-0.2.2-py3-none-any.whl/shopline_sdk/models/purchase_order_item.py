"""Shopline API 数据模型 - PurchaseOrderItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money



class Product_NameConfig(BaseModel):
    """Configuration model for product_name"""
    zh_hant: Optional[str] = Field(default=None, alias="zh-hant")
    en: Optional[str] = None


class Variation_TitlesItem(BaseModel):
    """Item model for variation_titles"""
    zh_hant: Optional[str] = Field(default=None, alias="zh-hant")
    en: Optional[str] = None


class Variation_NameConfig(BaseModel):
    """Configuration model for variation_name"""
    zh_hant: Optional[str] = Field(default=None, alias="zh-hant")
    en: Optional[str] = None

class PurchaseOrderItem(BaseModel):
    id: Optional[str] = None
    """Purchase Order Item ID 進貨單項目 ID"""
    product_id: Optional[str] = None
    """Product ID  產品 ID"""
    variation_id: Optional[str] = None
    """Variation ID 規格 ID"""
    product_name: Optional[Product_NameConfig] = None
    """Product Name 產品名稱"""
    variation_titles: Optional[List[Variation_TitlesItem]] = None
    variation_name: Optional[Variation_NameConfig] = None
    """Variation Name 規格內容"""
    image_url: Optional[str] = None
    """Image URL<br圖片網址"""
    sku: Optional[str] = None
    """Stock Keeping Unit 商品貨號"""
    gtin: Optional[str] = None
    """Global Trade Item Numbers 商品條碼編號"""
    total_quantity: Optional[int] = None
    """Total Quantity 進貨數量"""
    current_quantity: Optional[int] = None
    """Current Quantity 點收數量"""
    purchase_price: Optional[Money] = None
    supplier_id: Optional[str] = None
    """supplier_id 供應商 ID"""
    supplier_name: Optional[str] = None
    """supplier_name 供應商名稱"""
    subtotal: Optional[Money] = None
    price: Optional[Money] = None
    product_removed: Optional[bool] = None
    """Is Product Removed 商品是否已移除"""
    unlimited_quantity: Optional[bool] = None
    """Is Unlimited Quantity 是否為無限量庫存"""
    same_price: Optional[bool] = None
    """Same Price 價格是否相同"""
    total_stocks_cost: Optional[Money] = None
    stocks: Optional[Dict[str, Any]] = None
    """Stock 庫存"""