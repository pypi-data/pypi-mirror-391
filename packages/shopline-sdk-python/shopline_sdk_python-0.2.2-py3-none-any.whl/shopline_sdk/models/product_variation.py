"""Shopline API 数据模型 - ProductVariation"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .media import Media
from .money import Money
from .translatable_array import TranslatableArray



class Feed_VariationsConfig(BaseModel):
    """Configuration model for feed_variations"""
    color: Optional[Dict[str, Any]] = None
    size: Optional[Dict[str, Any]] = None
    material: Optional[str] = None

class ProductVariation(BaseModel):
    id: Optional[str] = None
    """Product Variation's ID 規格 ID"""
    fields_translations: Optional[TranslatableArray] = None
    price: Optional[Money] = None
    price_sale: Optional[Money] = None
    member_price: Optional[Money] = None
    retail_price: Optional[Money] = None
    cost: Optional[Money] = None
    quantity: Optional[float] = None
    """Product variation's current quantity 規格現有數量"""
    total_orderable_quantity: Optional[float] = None
    """Product variation's current orderable quantity 規格現有可購買數量"""
    unlimited_quantity: Optional[bool] = None
    """Whether the variation has unlimited quantity or not. 規格是否有無限數量 *Please check the main product's unlimited_quantity to see whether variation has unlimited quantity or not.  unlimited_quantity of variation will always shows null"""
    preorder_limit: Optional[int] = None
    """Pre-ordere Limit 預購上限"""
    media: Optional[Media] = None
    sku: Optional[str] = None
    """Stock Keeping Unit 貨號"""
    location_id: Optional[str] = None
    """Location ID 儲位編號"""
    feed_variations: Optional[Feed_VariationsConfig] = None
    """Default variations for product feed 廣告規格"""
    variant_option_ids: Optional[List[str]] = None
    """ID of the corresponding variant options 對應規格類別 ID"""
    barcode: Optional[str] = None
    """Barcode 商品條碼編號"""
    mpn: Optional[str] = None
    """Manufacturer Part Number 製造編號"""
    gtin: Optional[str] = None
    """Barcode 商品條碼編號"""
    barcode_type: Optional[Union[Literal['Code 128', 'Bookland EAN', 'ISBN'], str]] = None
    """Barcode type 商品條碼編號類別"""
    locked_inventory_count: Optional[float] = None
    weight: Optional[float] = None
    """Weight (kg) 重量 (公斤)"""