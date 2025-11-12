"""Shopline API 数据模型 - UpdateAddonProductBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .addon_product import AddonProduct
from .money import Money
from .translatable import Translatable



class Main_ProductsItem(BaseModel):
    """Item model for main_products"""
    id: Optional[str] = Field(default=None, alias="_id")
    addon_price: Optional[Money] = None

class UpdateAddonProductBody(BaseModel):
    """Payload for updating addon product"""
    title_translations: Optional[Translatable] = None
    media_ids: Optional[List[str]] = None
    unlimited_quantity: Optional[bool] = None
    start_at: Optional[str] = None
    """Addon Product start time 生效時間"""
    end_at: Optional[str] = None
    """Addon Product end time 過期時間"""
    main_products: Optional[List[Main_ProductsItem]] = None
    location_id: Optional[str] = None
    """custom location id"""
    tax_type: Optional[str] = None
    oversea_tax_type: Optional[str] = None
    sku: Optional[str] = None
    cost: Optional[Money] = None
    weight: Optional[float] = None
    quantity: Optional[float] = None