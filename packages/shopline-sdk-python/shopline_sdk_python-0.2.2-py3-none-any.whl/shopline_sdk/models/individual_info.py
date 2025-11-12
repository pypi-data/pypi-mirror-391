"""Shopline API 数据模型 - IndividualInfo"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class IndividualInfo(BaseModel):
    identity_number: Optional[str] = None
    """Identity number 身分證字號"""
    first_name: Optional[str] = None
    """First name 名字"""
    last_name: Optional[str] = None
    """Last name 姓氏"""