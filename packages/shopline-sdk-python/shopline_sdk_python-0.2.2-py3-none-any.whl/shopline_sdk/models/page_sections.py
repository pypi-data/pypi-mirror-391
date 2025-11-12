"""Shopline API 数据模型 - PageSections"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .page_section import PageSection


class PageSections(BaseModel):
    pass