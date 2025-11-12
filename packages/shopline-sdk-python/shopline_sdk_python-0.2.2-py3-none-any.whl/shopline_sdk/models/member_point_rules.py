"""Shopline API 数据模型 - MemberPointRules"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .member_point_rule import MemberPointRule


class MemberPointRules(BaseModel):
    pass