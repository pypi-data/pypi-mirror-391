"""Shopline API 数据模型 - CursorBasedPaginatable"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class CursorBasedPaginatable(BaseModel):
    last_id: Optional[str] = None
    """Last ID of result. 最後一筆 ID"""
    limit: Optional[int] = None
    """Numbers of result"""