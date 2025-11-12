"""Shopline API 数据模型 - PaymentConfigData"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class PaymentConfigData(BaseModel):
    shopline_payment_payment: Optional[Union[Literal['credit', 'specific_credit_types'], str]] = None
    """Shopline payment type Shopline payment 支援的付款方式"""
    installments: Optional[List[str]] = None
    """Installments 分期可選期數"""
    payment_subtype: Optional[str] = None
    """Payment Subtype 付款子類型"""