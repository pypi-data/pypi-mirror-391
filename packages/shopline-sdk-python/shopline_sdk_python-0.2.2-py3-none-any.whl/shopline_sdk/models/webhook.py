"""Shopline API 数据模型 - Webhook"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Webhook(BaseModel):
    id: Optional[str] = None
    """Webhook ID"""
    format: Optional[Union[Literal['json'], str]] = None
    """Webhook format Webhook格式 --- Currently support "json" only 現只支援"json" """
    address: Optional[str] = None
    """URL to receive the webhook 接收Webhook的URL"""
    status: Optional[Union[Literal['active', 'removed'], str]] = None
    """Webhook status Webhook狀態"""
    merchant_id: Optional[str] = None
    """Merchant ID 商户ID"""
    created_at: Optional[str] = None
    """Webhook created time Webhook創建日期"""
    updated_at: Optional[str] = None
    """Webhook updated time Webhook更新時間"""
    topics: Optional[List[Union[Literal['user/create', 'user/update', 'user/remove', 'user/sign_in', 'user/mobile_sign_in', 'user/mobile_sign_up', 'user/membership_tier_update', 'order/cancel', 'order/create', 'order/update', 'order/remove', 'order/pending', 'order/confirm', 'order/complete', 'order/status_notify_customer', 'order/product_detail_notify_customer', 'order/combine_orders', 'order/split_order', 'order_payment/update', 'order_payment/complete', 'order_payment/refund', 'order_payment/status_notify_customer', 'order_delivery/update', 'order_delivery/status_notify_customer', 'return_order/create', 'return_order/complete', 'return_order/cancel', 'pos_return_order/create', 'pos_return_order/update', 'page/create', 'page/update', 'product/create', 'product/update', 'product/remove', 'product/back_in_stock', 'product_review_comment/create', 'user_credit/create', 'user_credit/update', 'invoice/create', 'invoice/update', 'tax/create', 'tax/update', 'tax/remove', 'payment/create', 'payment/update', 'payment/remove', 'member_point/create', 'merchant/update', 'tag/create', 'tag/remove', 'persistent_cart/abandoned_cart', 'comment/payment_slip_upload', 'promotion/redeem', 'customer_group/update', 'customer_group/remove', 'warehouse/create', 'stock/update'], str]]] = None