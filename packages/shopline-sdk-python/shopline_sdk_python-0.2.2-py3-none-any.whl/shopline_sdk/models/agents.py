"""Shopline API 数据模型 - Agents"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .agent import Agent
from .paginatable import Paginatable


class Agents(BaseModel):
    items: Optional[List[Agent]] = None
    pagination: Optional[Paginatable] = None