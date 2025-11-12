"""Shopline API 数据模型 - LayoutSections"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .page_sections import PageSections


class LayoutSections(BaseModel):
    pass