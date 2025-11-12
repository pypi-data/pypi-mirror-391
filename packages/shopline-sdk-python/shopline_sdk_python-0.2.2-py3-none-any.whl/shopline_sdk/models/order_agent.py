"""Shopline API 数据模型 - OrderAgent"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class OrderAgent(BaseModel):
    email: Optional[str] = None
    """Email of the agent 員工電郵"""
    name: Optional[str] = None
    """Name of the agent 員工名稱"""
    phone: Optional[str] = None
    """Phone of the agent 員工電話號碼"""
    status: Optional[Union[Literal['active', 'removed'], str]] = None
    """Status of the agent 員工狀態"""