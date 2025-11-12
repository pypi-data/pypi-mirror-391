"""Shopline API 数据模型 - MediaUploadError"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class MediaUploadError(BaseModel):
    error: Optional[List[str]] = None
    """A detailed array of messages of the reason of failure"""