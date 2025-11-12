"""Shopline API 数据模型 - CreateAgentWorkLogRequestBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Work_LogConfig(BaseModel):
    """Configuration model for work_log"""
    clock_type: Union[Literal['in', 'out'], str]
    """The type of clock action (in or out)"""
    clocked_at: str
    """The timestamp of the clock action"""

class CreateAgentWorkLogRequestBody(BaseModel):
    """Payload for create agent's work log"""
    work_log: Work_LogConfig