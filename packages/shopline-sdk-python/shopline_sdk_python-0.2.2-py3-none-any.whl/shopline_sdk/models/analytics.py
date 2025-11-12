"""Shopline API 数据模型 - Analytics"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Analytics(BaseModel):
    start_date: Optional[str] = None
    """Starting date of the analytics 分析的開始日期"""
    end_date: Optional[str] = None
    """Ending date of the analytics 分析的終結日期"""