"""Shopline API 数据模型 - productIdsParam"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class productIdsParam(BaseModel):
    """Comma-separated product IDs for the query 用於查詢的逗號分隔產品 ID"""
    pass