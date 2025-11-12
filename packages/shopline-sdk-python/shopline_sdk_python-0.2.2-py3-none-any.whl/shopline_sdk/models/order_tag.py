"""Shopline API 数据模型 - OrderTag"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class OrderTag(BaseModel):
    content: Optional[str] = None
    """Text content of the tag 標籤內容"""