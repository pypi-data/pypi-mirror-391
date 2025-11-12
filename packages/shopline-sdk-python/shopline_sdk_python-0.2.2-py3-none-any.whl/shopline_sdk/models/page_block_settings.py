"""Shopline API 数据模型 - PageBlockSettings"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class PageBlockSettings(BaseModel):
    type: Optional[str] = None
    """The type of the block Block的類別"""
    settings: Optional[Dict[str, Union[str, float, int, bool, List[Any], Dict[str, Any]]]] = None
    """The settings of the block Block的設定"""