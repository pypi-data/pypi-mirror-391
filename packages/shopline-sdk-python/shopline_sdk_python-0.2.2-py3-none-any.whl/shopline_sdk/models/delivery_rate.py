"""Shopline API 数据模型 - DeliveryRate"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money


class DeliveryRate(BaseModel):
    fee: Optional[Money] = None
    rate_limit: Optional[float] = None
    countries: Optional[List[str]] = None
    delivery_areas: Optional[List[str]] = None
    fee_data: Optional[Dict[str, Any]] = None
    delivery_config: Optional[Dict[str, Any]] = None