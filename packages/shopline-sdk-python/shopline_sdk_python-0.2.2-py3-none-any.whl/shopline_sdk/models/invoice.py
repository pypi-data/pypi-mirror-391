"""Shopline API 数据模型 - Invoice"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Invoice(BaseModel):
    id: Optional[str] = None
    """Invocie ID 發票ID"""
    invoice_status: Optional[Union[Literal['active', 'cancel'], str]] = None
    """Invoice status 發票狀態 -  active 已開立  cancel 已作廢"""
    invoice_tax_type: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None