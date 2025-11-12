"""Shopline API 数据模型 - OrderActionLog"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class OrderActionLog(BaseModel):
    key: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    """data have mutiple ways to be presented according to its action log key.   根據key的不同，data的格式表達也會完全不一樣。"""
    created_at: Optional[str] = None
    performer_name: Optional[str] = None
    performer_type: Optional[str] = None
    performer_id: Optional[str] = None
    performing_application_id: Optional[str] = None