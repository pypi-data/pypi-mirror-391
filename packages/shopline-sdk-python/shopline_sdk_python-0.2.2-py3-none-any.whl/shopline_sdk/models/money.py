"""Shopline API 数据模型 - Money"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Money(BaseModel):
    cents: Optional[int] = None
    currency_symbol: Optional[str] = None
    currency_iso: Optional[str] = None
    label: Optional[str] = None
    dollars: Optional[float] = None