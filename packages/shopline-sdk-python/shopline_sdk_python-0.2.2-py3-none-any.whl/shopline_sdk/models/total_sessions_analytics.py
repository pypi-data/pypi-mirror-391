"""Shopline API 数据模型 - TotalSessionsAnalytics"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .analytics import Analytics



class MetadataConfig(BaseModel):
    """Configuration model for metadata"""
    all: Optional[float] = None
    """Total number of storefront views 網店瀏覽總量"""
    desktop: Optional[float] = None
    """Count of desktop-based views on the storefront Desktop網瀏覽總量"""
    mobile: Optional[float] = None
    """Count of mobile-based views on the storefront Mobile網店瀏覽總量"""


class RecordsItem(BaseModel):
    """Item model for records"""
    label: Optional[str] = None
    """Datetime of the data point 時間"""
    value: Optional[int] = None
    """Number of storefront views 網店瀏覽量"""

class TotalSessionsAnalytics(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    metadata: Optional[MetadataConfig] = None
    last_updated_at: Optional[str] = None
    """Most recent update time of the analytics database 分拆數據庫最後更新時間"""
    records: Optional[List[RecordsItem]] = None