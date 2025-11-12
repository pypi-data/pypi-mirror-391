"""Shopline API 数据模型 - MemberPoints"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .member_point import MemberPoint
from .paginatable import Paginatable


class MemberPoints(BaseModel):
    items: Optional[List[MemberPoint]] = None
    pagination: Optional[Paginatable] = None