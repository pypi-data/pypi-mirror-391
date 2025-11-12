"""Shopline API 数据模型 - PriceSets"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .price_set import PriceSet


class PriceSets(BaseModel):
    items: Optional[List[PriceSet]] = None