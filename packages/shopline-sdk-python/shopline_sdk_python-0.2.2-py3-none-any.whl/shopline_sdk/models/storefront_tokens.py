"""Shopline API 数据模型 - StorefrontTokens"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .storefront_token import StorefrontToken


class StorefrontTokens(BaseModel):
    items: Optional[List[StorefrontToken]] = None