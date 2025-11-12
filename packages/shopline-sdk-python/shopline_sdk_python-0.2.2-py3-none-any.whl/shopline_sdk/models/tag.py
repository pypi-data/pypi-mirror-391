"""Shopline API 数据模型 - Tag"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Tag(BaseModel):
    id: Optional[str] = None
    """ID"""
    content: Optional[str] = None
    """Text content of the tag 標籤內容"""
    owner_id: Optional[str] = None
    """Associated ID of the tag 標籤對應資源的ID"""
    owner_type: Optional[str] = None
    """Associated type of the tag 標籤對應資源的類別"""