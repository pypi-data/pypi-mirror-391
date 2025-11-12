"""Shopline API 数据模型 - FilterTag"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class FilterTag(BaseModel):
    id: Optional[str] = None
    """Filter Tag's ID 自訂篩選條件 ID"""
    name_translations: Optional[Translatable] = None