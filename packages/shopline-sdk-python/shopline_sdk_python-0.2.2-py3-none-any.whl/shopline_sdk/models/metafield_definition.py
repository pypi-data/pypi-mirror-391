"""Shopline API 数据模型 - MetafieldDefinition"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .metafield_value import MetafieldValue


class MetafieldDefinition(BaseModel):
    id: Optional[str] = None
    """Metafield definition ID"""
    namespace: Optional[str] = None
    key: Optional[str] = None
    name: Optional[str] = None
    """Name"""
    description: Optional[str] = None
    """description"""
    field_type: Optional[Union[Literal['single_line_text_field', 'multi_line_text_field', 'number_integer', 'number_decimal', 'json', 'boolean', 'url'], str]] = None
    merchant_id: Optional[str] = None
    """Merchant ID"""
    resource_type: Optional[Union[Literal['product', 'merchant', 'customer', 'order', 'order_item', 'cart_item'], str]] = None
    """Resource type of the metafield definition"""
    metafield_type: Optional[Union[Literal['merchant', 'app'], str]] = None
    """Type of metafield definition"""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None