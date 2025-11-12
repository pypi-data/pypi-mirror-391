"""Shopline API 数据模型 - PageSection"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .page_section_schema import PageSectionSchema


class PageSection(BaseModel):
    type: Optional[str] = None
    """The type of the page section. Page section 的種類"""
    schema_: Optional[PageSectionSchema] = Field(default=None, alias="schema")