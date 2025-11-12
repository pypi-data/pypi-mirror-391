"""Shopline API 数据模型 - ProductRevenue"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money


class ProductRevenue(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    sl_merchant_id: Optional[str] = None
    product_ids: Optional[List[str]] = None
    preset_revenue: Optional[Money] = None
    """預填銷售額"""
    preset_revenue_quantity: Optional[float] = None
    total_revenue: Optional[Money] = None
    """累計銷售額"""
    total_revenue_quantity: Optional[float] = None
    target_revenue: Optional[Money] = None
    """目標銷售額"""
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    status: Optional[Union[Literal['active', 'removed'], str]] = None