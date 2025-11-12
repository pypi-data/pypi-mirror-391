"""Shopline API 数据模型 - UpdateGiftBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .gift import Gift
from .translatable import Translatable


class UpdateGiftBody(BaseModel):
    """Payload for updating gift"""
    title_translations: Optional[Translatable] = None
    unlimited_quantity: Optional[bool] = None
    sku: Optional[str] = None
    cost: Optional[Translatable] = None
    weight: Optional[float] = None
    quantity: Optional[float] = None
    media_ids: Optional[List[str]] = None