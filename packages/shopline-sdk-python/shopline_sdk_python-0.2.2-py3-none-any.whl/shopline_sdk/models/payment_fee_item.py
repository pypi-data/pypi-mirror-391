"""Shopline API 数据模型 - PaymentFeeItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .pos_payment import PosPayment


class PaymentFeeItem(BaseModel):
    id: Optional[str] = None
    """Payment Fee Item ID"""
    order_id: Optional[str] = None
    """Order ID 訂單ID"""
    item_id: Optional[str] = None
    """Payment ID"""
    transaction_id: Optional[str] = None
    """Transaction ID"""
    item_type: Optional[str] = None
    item_price: Optional[Money] = None
    quantity: Optional[int] = None
    """Quantity 數量"""
    section_type: Optional[str] = None
    total: Optional[Money] = None
    item_owner_id: Optional[str] = None
    """Merchant ID 商户ID"""
    item_owner_type: Optional[str] = None
    object_data: Optional[PosPayment] = None
    """Snapshot of payment 支付快照"""