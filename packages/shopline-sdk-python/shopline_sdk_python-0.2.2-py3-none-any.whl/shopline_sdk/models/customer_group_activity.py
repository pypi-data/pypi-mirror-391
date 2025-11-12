"""Shopline API 数据模型 - CustomerGroupActivity"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class CustomerGroupActivity(BaseModel):
    id: Optional[str] = None
    name_translations: Optional[Translatable] = None
    """Activity Name 活動名稱"""
    activity_status: Optional[Union[Literal['draft', 'pending', 'cancelled', 'sending', 'sent', 'failed', 'partially_sent', 'removed'], str]] = None
    """The activity status of the customer group. 此活動目前的狀態"""
    status: Optional[Union[Literal['active', 'removed'], str]] = None
    """The status of the customer group. 此筆紀錄的狀態"""
    ref_id: Optional[str] = None
    """Reference ID of the activity. 關聯此活動的外部ID"""
    type: Optional[str] = None
    """Type of the activity. 此活動的類別"""
    activity_time: Optional[str] = None
    submitted_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    """The created way for the activity. 此筆活動紀錄的建立來源"""