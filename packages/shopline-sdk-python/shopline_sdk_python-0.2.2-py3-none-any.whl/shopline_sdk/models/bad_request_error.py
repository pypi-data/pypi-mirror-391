"""Shopline API 数据模型 - BadRequestError"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class BadRequestError(BaseModel):
    error: Optional[str] = None
    """A detailed message of the reason of failure"""
    code: Optional[str] = None
    """An error code"""
    caused_by: Optional[Dict[str, Any]] = None
    """An extra information of the reason of failure"""