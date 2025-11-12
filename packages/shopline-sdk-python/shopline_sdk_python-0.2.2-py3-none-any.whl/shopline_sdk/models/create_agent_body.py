"""Shopline API 数据模型 - CreateAgentBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .agent import Agent


class CreateAgentBody(BaseModel):
    """Payload for creating agent"""
    name: str
    pin_code: str
    """Pin code of the agent 員工 pin code"""
    email: Optional[str] = None
    phone: Optional[str] = None