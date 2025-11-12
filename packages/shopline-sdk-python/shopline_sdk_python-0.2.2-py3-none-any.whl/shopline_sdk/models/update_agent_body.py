"""Shopline API 数据模型 - UpdateAgentBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .agent import Agent


class UpdateAgentBody(BaseModel):
    """Payload for updating agent"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None