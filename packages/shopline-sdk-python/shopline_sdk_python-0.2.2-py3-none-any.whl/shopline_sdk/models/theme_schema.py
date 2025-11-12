"""Shopline API 数据模型 - ThemeSchema"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable



class ItemsConfig(BaseModel):
    """Configuration model for items"""
    name: Optional[Translatable] = None
    settings: Optional[Dict[str, Any]] = None
    """Settings of the item of theme schema"""

class ThemeSchema(BaseModel):
    items: Optional[ItemsConfig] = None