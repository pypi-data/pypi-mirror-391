"""Shopline API 数据模型 - MaxApplicableMemberPoint"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .member_point_rule import MemberPointRule


class MaxApplicableMemberPoint(BaseModel):
    max_applicable_member_point_redeem_to_cash: Optional[int] = None
    """The maximum member point the user can apply to the order transfers to dollars"""
    max_applicable_member_point: Optional[int] = None
    """The maximum member point the user can apply to the order"""
    point_redeem_to_cash_rule: Optional[MemberPointRule] = None