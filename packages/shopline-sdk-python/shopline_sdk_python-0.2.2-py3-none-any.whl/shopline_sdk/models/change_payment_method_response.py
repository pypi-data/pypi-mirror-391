"""Shopline API 数据模型 - ChangePaymentMethodResponse"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .order import Order
from .transaction import Transaction


class ChangePaymentMethodResponse(BaseModel):
    order: Optional[Order] = None
    transactions: Optional[List[Transaction]] = None