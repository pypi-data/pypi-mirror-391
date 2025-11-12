"""Shopline API 数据模型 - ProductFeedSettings"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .paginatable import Paginatable
from .product_feed_setting import ProductFeedSetting


class ProductFeedSettings(BaseModel):
    items: Optional[List[ProductFeedSetting]] = None
    pagination: Optional[Paginatable] = None