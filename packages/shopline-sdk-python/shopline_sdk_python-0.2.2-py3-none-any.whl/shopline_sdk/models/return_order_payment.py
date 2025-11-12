"""Shopline API 数据模型 - ReturnOrderPayment"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money


class ReturnOrderPayment(BaseModel):
    id: Optional[Any] = None
    """Order Payment ID"""
    payment_method_id: Optional[str] = None
    """Payment Method ID 付款方式ID"""
    payment_type: Optional[Union[Literal['ecpay', 'bank_transfer', 'cash_on_delivery', 'custom', 'tw_711_b2c_pay', 'tw_711_pay', 'sl_logistics_ninjavan_cod', 'sl_logistics_kerry_th_cod', 'sl_logistics_ghtk_cod', 'sl_logistics_janio_cod', 'sl_logistics_poslaju_cod'], str]] = None
    """Payment Method 付款方式"""
    status: Optional[Union[Literal['pending', 'failed', 'expired', 'completed', 'refunding', 'refunded'], str]] = None
    """Payment Status 付款狀態   Payment status allows:  pending 未付款  failed 付款失敗  expired 超過付款時間  completed 已付款  refunding 退款中  refunded 已退款"""
    updated_at: Optional[str] = None
    """Updated Time related to change of payment 付款更新時間 (UTC +0)"""
    created_at: Optional[str] = None
    """Created Date 創造時間 (UTC +0)"""
    refund_amount: Optional[Money] = None
    update_refund_amount_at: Optional[str] = None
    """Update refund_amount Date 退款金額更新時間 (UTC +0)"""
    payment_data: Optional[Dict[str, Any]] = None
    """Payment Details Info 付款詳細資訊 (如有串接第三方金流)  Please refer to the example below"""