"""Shopline API 数据模型 - EntityRenderError"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class EntityRenderError(BaseModel):
    """Unprocessable entity"""
    message: Optional[str] = None
    code: Optional[str] = None