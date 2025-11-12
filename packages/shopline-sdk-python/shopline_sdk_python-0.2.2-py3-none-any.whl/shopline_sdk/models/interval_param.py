"""Shopline API 数据模型 - intervalParam"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class intervalParam(BaseModel):
    """Interval type 時間單位"""
    value: Literal['days', 'hours', 'hour_of_day', 'day_of_week', 'months', 'quarters']
    """Enum values: days, hours, hour_of_day, day_of_week, months, quarters"""