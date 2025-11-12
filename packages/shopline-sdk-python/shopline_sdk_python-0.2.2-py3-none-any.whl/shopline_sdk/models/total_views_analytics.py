"""Shopline API 数据模型 - TotalViewsAnalytics"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .analytics import Analytics



class MetadataConfig(BaseModel):
    """Configuration model for metadata"""
    total: Optional[float] = None
    """Total number of storefront views 網店瀏覽總量"""


class RecordsItem(BaseModel):
    """Item model for records"""
    label: Optional[str] = None
    """Datetime of the data point 時間"""
    value: Optional[int] = None
    """Number of storefront views 網店瀏覽量"""

class TotalViewsAnalytics(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    metadata: Optional[MetadataConfig] = None
    records: Optional[List[RecordsItem]] = None