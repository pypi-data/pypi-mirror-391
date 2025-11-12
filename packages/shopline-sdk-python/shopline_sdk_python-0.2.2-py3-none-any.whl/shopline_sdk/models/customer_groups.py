"""Shopline API 数据模型 - CustomerGroups"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .customer_group import CustomerGroup
from .paginatable import Paginatable


class CustomerGroups(BaseModel):
    pagination: Optional[Paginatable] = None
    items: Optional[List[CustomerGroup]] = None