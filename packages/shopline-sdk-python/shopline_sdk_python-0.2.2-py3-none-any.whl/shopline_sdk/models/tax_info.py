"""Shopline API 数据模型 - TaxInfo"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class TaxInfo(BaseModel):
    min: Optional[float] = None
    """Max rate 套用最低稅率"""
    max: Optional[float] = None
    """Min rate 套用最高稅率"""
    country_code: Optional[str] = None
    """ISO Country Code 稅收國家或地區（ISO 標準國家代碼）"""
    flag: Optional[str] = None
    """Flag 國家旗幟"""
    region: Optional[str] = None
    """Tax Region 稅收地區"""
    city: Optional[str] = None
    """City 城市"""
    name: Optional[str] = None
    """Tax Name 稅金名稱"""