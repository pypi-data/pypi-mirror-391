"""Shopline API 数据模型 - GlobalSection"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .global_section_settings import GlobalSectionSettings


class GlobalSection(BaseModel):
    pass