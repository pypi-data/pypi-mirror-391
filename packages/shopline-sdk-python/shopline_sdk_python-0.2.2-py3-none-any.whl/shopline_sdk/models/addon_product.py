"""Shopline API 数据模型 - AddonProduct"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .media import Media
from .money import Money
from .translatable import Translatable



class PromotionsItem(BaseModel):
    """Item model for promotions"""
    id: Optional[str] = None
    """Promotion ID 優惠活動ID"""
    discounted_price: Optional[Money] = None
    start_at: Optional[str] = None
    """Promotion start time 活動開始時間"""
    end_at: Optional[str] = None
    """Promotion end time 活動結束時間 - null = no end date 永不過期"""
    conditions: Optional[List[Dict[str, Any]]] = None
    """本階層活動生效條件"""

class AddonProduct(BaseModel):
    id: Optional[str] = None
    """Add-on Product‘s ID 加購品ID"""
    status: Optional[Union[Literal['active', 'draft'], str]] = None
    """Add-on Product's Status 加購品狀態 - Status: active上架 draft 下架"""
    title_translations: Optional[Translatable] = None
    price: Optional[float] = None
    """Addon Product Price 加購品價格"""
    weight: Optional[float] = None
    """Addon Product's Weight (kg) 加購品重量 (公斤)"""
    quantity: Optional[float] = None
    """Current Quantity 加購品目前庫存"""
    unlimited_quantity: Optional[bool] = None
    """Unlimited quantity or not. 加購品數量是否無限  -  true: unlimited quantity  false: limited quantity"""
    medias: Optional[Media] = None
    sku: Optional[str] = None
    """Stock Keeping Unit 加購品貨號"""
    tax_type: Optional[str] = None
    """Tax Type 國內稅項"""
    oversea_tax_type: Optional[str] = None
    """Oversea Tax Type 海外稅項"""
    created_at: Optional[str] = None
    """Created Time 加購品創造時間"""
    promotions: Optional[List[PromotionsItem]] = None
    """Promotions 加購活動  Only provided when include_fields contains 'promotions'  僅於include_fields傳入 'promotions' 時提供"""