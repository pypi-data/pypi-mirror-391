"""Shopline API 数据模型 - TopProductsAnalytics"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .analytics import Analytics
from .paginatable import Paginatable
from .top_products_analytics_record import TopProductsAnalyticsRecord


class TopProductsAnalytics(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    timezone: Optional[int] = None
    """Timezone offset 時區時差"""
    pagination: Optional[Paginatable] = None
    records: Optional[List[TopProductsAnalyticsRecord]] = None