"""Shopline API 数据模型 - ProductStock"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable
from .translatable_array import TranslatableArray



class StocksConfig(BaseModel):
    """Configuration model for stocks"""
    warehouse_id: Optional[str] = None
    quantity: Optional[int] = None


class VariationsConfig(BaseModel):
    """Configuration model for variations"""
    id: Optional[str] = None
    fields_translations: Optional[TranslatableArray] = None
    stocks: Optional[Dict[str, Any]] = None

class ProductStock(BaseModel):
    id: Optional[str] = None
    """Product's ID 商品ID"""
    title_translations: Optional[Translatable] = None
    unlimited_quantity: Optional[bool] = None
    """Unlimited product quantity or not. 商品數量是否無限"""
    stocks: Optional[StocksConfig] = None
    """Product's Stock 庫存"""
    variations: Optional[VariationsConfig] = None
    """Product's Variation 規格品"""