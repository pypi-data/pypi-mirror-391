"""Shopline API 数据模型 - AgentWorkLog"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class In_LogConfig(BaseModel):
    """Configuration model for in_log"""
    id: Optional[int] = None
    agent_id: Optional[int] = None
    clock_type: Optional[Union[Literal['in', 'out'], str]] = None
    clocked_at: Optional[str] = None
    created_at: Optional[str] = None


class Out_LogConfig(BaseModel):
    """Configuration model for out_log"""
    id: Optional[int] = None
    agent_id: Optional[int] = None
    clock_type: Optional[Union[Literal['in', 'out'], str]] = None
    clocked_at: Optional[str] = None
    created_at: Optional[str] = None

class AgentWorkLog(BaseModel):
    in_log: Optional[In_LogConfig] = None
    out_log: Optional[Out_LogConfig] = None
    range: Optional[int] = None
    """Duration in seconds between in_log and out_log"""