"""Shopline API 数据模型 - OrderActionLogs"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .order_action_log import OrderActionLog


class OrderActionLogs(BaseModel):
    items: Optional[List[OrderActionLog]] = None