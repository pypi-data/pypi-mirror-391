"""Shopline API 数据模型 - AddonProducts"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .addon_product import AddonProduct
from .paginatable import Paginatable


class AddonProducts(BaseModel):
    pagination: Optional[Paginatable] = None
    items: Optional[List[AddonProduct]] = None