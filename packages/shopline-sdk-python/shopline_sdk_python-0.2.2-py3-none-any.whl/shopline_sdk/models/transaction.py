"""Shopline API 数据模型 - Transaction"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .agent import Agent
from .money import Money
from .pos_payment import PosPayment


class Transaction(BaseModel):
    id: Optional[str] = None
    """Transaction ID"""
    change: Optional[Money] = None
    total: Optional[Money] = None
    payments: Optional[List[PosPayment]] = None
    """Transaction Payment methods"""
    transaction_number: Optional[str] = None
    """Transaction Number"""
    type: Optional[str] = None
    """Transaction Type"""
    payment_status: Optional[str] = None
    """Transaction Payment Status"""
    delivery_status: Optional[str] = None
    """Transaction Delivery Status"""
    channel_id: Optional[str] = None
    """Channel ID"""
    order_id: Optional[str] = None
    """Order ID"""
    note: Optional[str] = None
    """Note"""
    created_at: Optional[str] = None
    """Transaction Created Time"""
    updated_at: Optional[str] = None
    """Transaction Updated Time"""
    conflict_group_id: Optional[str] = None
    """Transaction Conflict Group Id"""
    status: Optional[str] = None
    """Transaction Status"""
    agent: Optional[Agent] = None
    """Transaction Agent   操作人員"""
    order_number: Optional[str] = None
    """Order Number"""
    order_status: Optional[Union[Literal['removed', 'confirmed', 'completed', 'cancelled'], str]] = None
    """Order Status"""
    tax_id: Optional[str] = None
    """統一編號"""
    tax_type: Optional[str] = None
    """Tax Type"""
    invoice_ids: Optional[List[str]] = None
    """Invoice IDs"""
    invoice_type: Optional[str] = None
    """Invoice Type"""
    invoice_status: Optional[str] = None
    """Invoice Status"""
    invoice_created_at: Optional[str] = None
    """Invoice Created Time"""
    invoice_cancelled_at: Optional[str] = None
    """Invoice Cancelled Time"""
    invoice_created_by: Optional[str] = None
    """Invoice Created By"""
    invoice_total_amount: Optional[int] = None
    """Invoice Total Amount"""