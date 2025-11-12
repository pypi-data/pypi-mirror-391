"""Shopline API 数据模型 - Agent"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Agent(BaseModel):
    id: Optional[str] = None
    """Id of the agent 員工ID"""
    email: Optional[str] = None
    """Email of the agent 員工電郵"""
    name: Optional[str] = None
    """Name of the agent 員工名稱"""
    phone: Optional[str] = None
    """Phone of the agent 員工電話號碼"""
    is_working: Optional[bool] = None
    """Working status of the agent 員工工作狀態（上班/下班）"""
    channel_ids: Optional[List[Any]] = None
    """Staff's store IDs 員工所有的門市"""