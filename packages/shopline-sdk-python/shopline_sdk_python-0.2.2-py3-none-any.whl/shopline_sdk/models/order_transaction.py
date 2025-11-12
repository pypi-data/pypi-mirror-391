"""Shopline API 数据模型 - OrderTransaction"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .agent import Agent
from .pos_payment import PosPayment


class OrderTransaction(BaseModel):
    invoice_date: Optional[str] = None
    """Invoice Created Time"""
    tax_id: Optional[str] = None
    """統一編號"""
    invoice_cancelled_at: Optional[str] = None
    """Invoice Cancelled Time"""
    transaction_number: Optional[str] = None
    """Transaction Number"""
    created_at: Optional[str] = None
    """Transaction Created Time"""
    payments: Optional[List[PosPayment]] = None
    """Transaction Payment methods"""
    invoice_number: Optional[List[str]] = None
    """Invoice numbers"""
    agent: Optional[Agent] = None
    """Transaction Agent   操作人員"""
    order_number: Optional[List[str]] = None
    """Order Number"""
    note: Optional[str] = None
    """Note"""