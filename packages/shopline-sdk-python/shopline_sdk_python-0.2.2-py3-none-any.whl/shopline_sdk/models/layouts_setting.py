"""Shopline API 数据模型 - LayoutsSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .global_section_settings import GlobalSectionSettings


class LayoutsSetting(BaseModel):
    announcement: Optional[GlobalSectionSettings] = None
    header: Optional[GlobalSectionSettings] = None
    footer: Optional[GlobalSectionSettings] = None