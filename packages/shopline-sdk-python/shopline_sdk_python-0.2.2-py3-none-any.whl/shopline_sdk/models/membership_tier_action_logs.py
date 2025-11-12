"""Shopline API 数据模型 - MembershipTierActionLogs"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .membership_tier_action_log import MembershipTierActionLog
from .paginatable import Paginatable


class MembershipTierActionLogs(BaseModel):
    items: Optional[List[MembershipTierActionLog]] = None
    pagination: Optional[Paginatable] = None