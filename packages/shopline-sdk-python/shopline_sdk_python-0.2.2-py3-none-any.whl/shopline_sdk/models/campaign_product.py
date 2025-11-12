"""Shopline API 数据模型 - CampaignProduct"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money


class CampaignProduct(BaseModel):
    id: Optional[str] = None
    """Affiliate Campaign Unique ID 推薦活動ID"""
    product_id: Optional[str] = None
    """Product ID 商品ID"""
    affiliate_percentage: Optional[float] = None
    """Affiliate percentage 分潤百分比"""
    affiliate_amount: Optional[Money] = None