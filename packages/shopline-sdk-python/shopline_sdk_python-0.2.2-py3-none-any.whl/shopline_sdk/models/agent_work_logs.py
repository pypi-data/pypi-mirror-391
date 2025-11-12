"""Shopline API 数据模型 - AgentWorkLogs"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .agent_work_log import AgentWorkLog


class AgentWorkLogs(BaseModel):
    items: Optional[List[AgentWorkLog]] = None