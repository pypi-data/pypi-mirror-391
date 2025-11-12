"""Shopline API 数据模型 - PriceDetail"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money


class PriceDetail(BaseModel):
    variation_key: Optional[str] = None
    """ProductVariation's ID 商品規格ID"""
    price: Optional[Money] = None
    price_sale: Optional[Money] = None