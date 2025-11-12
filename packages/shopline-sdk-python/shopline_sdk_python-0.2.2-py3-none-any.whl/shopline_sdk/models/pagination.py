"""Shopline API 数据模型 - pagination"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .paginatable import Paginatable


class pagination(BaseModel):
    pass