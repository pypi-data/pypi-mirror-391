"""Shopline API 数据模型 - AddressPreferences"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .address_preference import AddressPreference


class AddressPreferences(BaseModel):
    country: Optional[str] = None
    scope: Optional[str] = None
    max_priority: Optional[int] = None
    """The max priority of preferences 地址格式參考的 priority 最大值，填寫順序最優先的參考"""
    preferences: Optional[List[AddressPreference]] = None