"""Shopline API 数据模型 - OrderPayment"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .translatable import Translatable


class OrderPayment(BaseModel):
    payment_method_id: Optional[str] = None
    """Payment Method ID 付款方式ID"""
    ref_payment_id: Optional[str] = None
    """3rd party payment reference ID"""
    payment_type: Optional[Union[Literal['ecpay', 'bank_transfer', 'cash_on_delivery', 'custom tw_711_b2c_pay', 'tw_711_pay', 'sl_logistics_ninjavan_cod', 'sl_logistics_kerry_th_cod', 'sl_logistics_ghtk_cod', 'sl_logistics_janio_cod', 'sl_logistics_poslaju_cod'], str]] = None
    """Payment Method 付款方式"""
    name_translations: Optional[Translatable] = None
    status: Optional[Union[Literal['pending', 'failed', 'expired', 'completed', 'refunding', 'refunded'], str]] = None
    """Payment Status 付款狀態   Payment status allows:  pending 未付款  failed 付款失敗  expired 超過付款時間  completed 已付款  refunding 退款中  refunded 已退款"""
    payment_fee: Optional[Money] = None
    total: Optional[Money] = None
    paid_at: Optional[str] = None
    """Paid Time 付款完成時間 (UTC +0)"""
    updated_at: Optional[str] = None
    """Updated Time related to change of payment 付款更新時間 (UTC +0)"""
    created_at: Optional[str] = None
    """Created Date 訂單創造時間 (UTC +0)"""
    payment_data: Optional[Dict[str, Any]] = None
    """Payment Details Info 付款詳細資訊 (如有串接第三方金流)  Please refer to the example below"""
    last_four_digits: Optional[str] = None
    """Credit Card Last Four Digits. 信用卡後四碼"""
    payment_slips_setting: Optional[Dict[str, Any]] = None
    """Setting for payment slips. 付款明細設定"""
    shopline_payment_payment: Optional[str] = None
    expire_time: Optional[float] = None
    """Expiry time of the payment, in days. 失效時間，以天作為單位。"""