"""Shopline API 数据模型 - MultipassLinkings"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .multipass_linking import MultipassLinking


class MultipassLinkings(BaseModel):
    result: Optional[str] = None
    """operation result"""
    linkings: Optional[List[MultipassLinking]] = None
    next: Optional[str] = None
    """for pagination on next call, return items since this ID"""