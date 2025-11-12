"""Shopline API 数据模型 - NetOrdersAnalytics"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .analytics import Analytics



class MetadataConfig(BaseModel):
    """Configuration model for metadata"""
    total: Optional[float] = None
    """Net number of orders 訂單總量"""


class RecordsItem(BaseModel):
    """Item model for records"""
    label: Optional[str] = None
    """Datetime of the data point 時間"""
    value: Optional[int] = None
    """Net number of orders 訂單量"""

class NetOrdersAnalytics(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    metadata: Optional[MetadataConfig] = None
    records: Optional[List[RecordsItem]] = None