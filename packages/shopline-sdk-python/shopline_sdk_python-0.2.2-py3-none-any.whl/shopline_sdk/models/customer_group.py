"""Shopline API 数据模型 - CustomerGroup"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class CustomerGroup(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    count: Optional[float] = None
    """The customer group user count. 分群顧客人數"""
    email_users_count: Optional[float] = None
    """Email count of the customer group. 分群中有email的人數"""
    mobile_phone_users_count: Optional[float] = None
    """Mobile phone count of the customer group. 分群中有手機的人數"""
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    status: Optional[Union[Literal['active', 'expired'], str]] = None
    update_type: Optional[Union[Literal['manual', 'auto'], str]] = None
    """The updated way. 更新方式"""
    update_cycle: Optional[float] = None
    """The updated cycle in days. 更新週期（天數）"""
    created_by: Optional[Union[Literal['manual', 'auto'], str]] = None
    """The updated way only for child customer group. 子分群更新方式"""
    parent_id: Optional[str] = None
    """ID of parent customer group. 母分群的ID"""
    last_child_id: Optional[str] = None
    """last child id. 最新子分群的ID"""
    last_updated_at: Optional[str] = None
    next_update_at: Optional[str] = None
    expired_at: Optional[str] = None
    """The expired time of the customer group. 此分群的過期時間"""