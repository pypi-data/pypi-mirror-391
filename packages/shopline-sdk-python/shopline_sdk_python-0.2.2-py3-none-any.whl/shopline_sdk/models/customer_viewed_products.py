"""Shopline API 数据模型 - CustomerViewedProducts"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .customer_viewed_product import CustomerViewedProduct
from .paginatable import Paginatable


class CustomerViewedProducts(BaseModel):
    items: Optional[List[CustomerViewedProduct]] = None
    pagination: Optional[Paginatable] = None