"""Shopline API 数据模型 - DeliveryTimeSlot"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class DeliveryTimeSlot(BaseModel):
    id: Optional[str] = None
    """DeliveryTimeSlot ID 運送時段ID"""
    group_key: Optional[str] = None
    limit: Optional[int] = None
    """Limit of the time slot 運送時段限制次數"""
    translations: Optional[Translatable] = None
    weekday: Optional[int] = None
    """Specific weekday"""
    status: Optional[str] = None
    """Time slot status 運送時段狀態"""
    created_at: Optional[str] = None
    """Created Time 建立時間"""
    updated_at: Optional[str] = None
    """Updated Time 更新時間"""
    is_available: Optional[bool] = None
    """Is available 運送時段是否可選"""