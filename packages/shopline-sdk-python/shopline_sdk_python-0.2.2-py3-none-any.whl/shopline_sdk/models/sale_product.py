"""Shopline API 数据模型 - SaleProduct"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class VariationsItem(BaseModel):
    """Item model for variations"""
    variation_id: Optional[str] = None
    custom_keys: Optional[List[str]] = None

class SaleProduct(BaseModel):
    product_id: Optional[str] = None
    custom_numbers: Optional[List[str]] = None
    custom_keys: Optional[List[str]] = None
    effective_key: Optional[bool] = None
    create_time: Optional[str] = None
    update_time: Optional[str] = None
    variations: Optional[List[VariationsItem]] = None