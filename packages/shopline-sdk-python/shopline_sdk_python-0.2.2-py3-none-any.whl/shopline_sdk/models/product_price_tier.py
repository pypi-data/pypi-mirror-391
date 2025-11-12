"""Shopline API 数据模型 - ProductPriceTier"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money


class ProductPriceTier(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    """Product price tier's ID 產品價格分級的ID"""
    created_at: Optional[str] = None
    """Product price tier's created time 產品價格分級的創建時間"""
    updated_at: Optional[str] = None
    """Product price tier's updated time 產品價格分級的更新時間"""
    member_price: Optional[Money] = None
    membership_tier_id: Optional[str] = None
    """Membership tier's ID 會員等級ID"""
    product_id: Optional[str] = None
    """Product's ID 商品ID"""
    status: Optional[Union[Literal['active'], str]] = None
    """Product price tier's status 產品價格分級的狀態"""
    variation_key: Optional[str] = None
    """Product variation's ID 產品規格的ID"""