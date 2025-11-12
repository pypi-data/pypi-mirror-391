"""Shopline API 数据模型 - TaxRegion"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class TaxRegion(BaseModel):
    id: Optional[str] = None
    """Tax region ID 稅務地區ID"""
    region: Optional[str] = None
    """Tax region 稅務地區"""
    rate: Optional[float] = None
    """Tax rate 稅率"""
    type: Optional[str] = None
    """Tax type 稅別"""
    default_rate: Optional[float] = None
    """Default tax rate 預設稅率"""
    default_rate_range: Optional[List[float]] = None
    """Default tax rate range 預設稅率範圍"""