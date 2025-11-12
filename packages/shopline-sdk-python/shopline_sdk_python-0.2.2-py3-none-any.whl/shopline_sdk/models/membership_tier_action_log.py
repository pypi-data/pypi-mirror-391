"""Shopline API 数据模型 - MembershipTierActionLog"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class MembershipTierActionLog(BaseModel):
    key: Optional[Union[Literal['updated_user_membership_tier', 'extended_user_membership_tier'], str]] = None
    data: Optional[Dict[str, Any]] = None
    """data have mutiple ways to be presented according to its action log key.   根據key的不同，data的格式表達也會完全不一樣。"""
    merchant_id: Optional[str] = None
    status: Optional[str] = None
    performer_name: Optional[str] = None
    performer_type: Optional[str] = None
    performer_id: Optional[str] = None
    target_ids: Optional[List[str]] = None
    target_type: Optional[str] = None
    created_at: Optional[str] = None