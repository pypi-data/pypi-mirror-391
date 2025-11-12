"""Shopline API 数据模型 - NotFoundError"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class NotFoundError(BaseModel):
    message: Optional[str] = None
    code: Optional[str] = None
    extras: Optional[Dict[str, Any]] = None
    """Optional, Extra information about the error"""