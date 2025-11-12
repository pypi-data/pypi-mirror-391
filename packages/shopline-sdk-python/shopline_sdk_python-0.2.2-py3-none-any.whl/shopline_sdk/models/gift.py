"""Shopline API 数据模型 - Gift"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .media import Media
from .product_variation import ProductVariation
from .translatable import Translatable



class Field_TitlesItem(BaseModel):
    """Item model for field_titles"""
    key: Optional[str] = None
    label: Optional[str] = None
    name_translations: Optional[Translatable] = None


class Variant_OptionsItem(BaseModel):
    """Item model for variant_options"""
    id: Optional[str] = None
    name_translations: Optional[Translatable] = None
    type: Optional[Union[Literal['color', 'size', 'custom_1', 'custom_2', 'custom_3'], str]] = None
    media: Optional[Dict[str, Any]] = None
    index: Optional[int] = None

class Gift(BaseModel):
    id: Optional[str] = None
    """Gift ID 贈品ID"""
    status: Optional[Union[Literal['active', 'draft'], str]] = None
    """Gift's Status 贈品狀態"""
    title_translations: Optional[Translatable] = None
    sku: Optional[str] = None
    """Stock Keeping Unit 贈品貨號"""
    quantity: Optional[float] = None
    """Current Quantity 贈品目前庫存"""
    cost: Optional[Translatable] = None
    weight: Optional[float] = None
    """Weight of Gift (kg) 贈品重量 (公斤重)"""
    medias: Optional[Media] = None
    unlimited_quantity: Optional[bool] = None
    """Unlimited gift quantity or not. 贈品數量是否無限"""
    updated_at: Optional[str] = None
    """Updated Time 贈品更新時間"""
    created_at: Optional[str] = None
    """Created Time 贈品創造時間"""
    variations: Optional[List[ProductVariation]] = None
    """Product Variations Data 商品規格資訊"""
    field_titles: Optional[List[Field_TitlesItem]] = None
    """Field Title Data 規格名稱"""
    variant_options: Optional[List[Variant_OptionsItem]] = None
    """Product Variations 商品規格 -  Maximum 3 types of variant option for a product, type allow (color, size, custom_1, custom_2, custom_3)  最多支援三種不同的 type, type 支援(color, size, custom_1, custom_2, custom_3)"""