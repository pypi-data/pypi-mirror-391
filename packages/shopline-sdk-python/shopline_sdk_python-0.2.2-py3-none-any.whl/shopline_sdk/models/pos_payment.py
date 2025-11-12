"""Shopline API 数据模型 - PosPayment"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .translatable import Translatable


class PosPayment(BaseModel):
    id: Optional[str] = None
    """Payment Method ID 付款方式ID"""
    instructions_translations: Optional[Translatable] = None
    name_translations: Optional[Translatable] = None
    type: Optional[str] = None
    """Payment's Type 付款方式代碼"""
    amount: Optional[Money] = None