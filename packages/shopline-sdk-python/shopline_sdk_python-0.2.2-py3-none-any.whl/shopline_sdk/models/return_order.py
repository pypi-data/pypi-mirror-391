"""Shopline API 数据模型 - ReturnOrder"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .order_promotion_item import OrderPromotionItem
from .return_order_delivery import ReturnOrderDelivery
from .return_order_delivery_address import ReturnOrderDeliveryAddress
from .return_order_delivery_data import ReturnOrderDeliveryData
from .return_order_item import ReturnOrderItem
from .return_order_payment import ReturnOrderPayment
from .return_order_promotion_item import ReturnOrderPromotionItem
from .return_order_ref_data import ReturnOrderRefData



class OrderConfig(BaseModel):
    """Configuration model for order"""
    id: Optional[str] = Field(default=None, alias="_id")
    """order id 訂單ID"""
    order_number: Optional[str] = None
    """Order Number 訂單號碼"""
    merchant_order_number: Optional[str] = None
    """店家自定義訂單號 (會根據rollout_key選擇用哪個order_number)"""

class ReturnOrder(BaseModel):
    id: Optional[str] = None
    """Return order ID"""
    return_order_number: Optional[str] = None
    """Return order number 退貨單號"""
    created_at: Optional[str] = None
    """Return order created time 退貨單創建日期"""
    updated_at: Optional[str] = None
    """Return order updated time 退貨單更新時間"""
    status: Optional[Union[Literal['confirmed', 'completed', 'cancelled'], str]] = None
    """status 退貨訂單狀態"""
    total: Optional[Money] = None
    order_id: Optional[str] = None
    """Order ID"""
    delivery_address: Optional[ReturnOrderDeliveryAddress] = None
    inspect_status: Optional[Union[Literal['pending', 'inspected'], str]] = None
    """Inspect status 驗貨狀態"""
    customer_id: Optional[str] = None
    """Customer ID 顧客ID"""
    customer_name: Optional[str] = None
    """Customer's Name 顧客姓名"""
    customer_email: Optional[str] = None
    """Customer's Email 顧客Email"""
    customer_phone: Optional[str] = None
    """Customer's Phone 顧客電話"""
    order_delivery: Optional[ReturnOrderDelivery] = None
    delivery_data: Optional[ReturnOrderDeliveryData] = None
    order_payment: Optional[ReturnOrderPayment] = None
    order_payment_status: Optional[Union[Literal['pending', 'refunded'], str]] = None
    """order payment status 訂單退款狀態"""
    order_delivery_status: Optional[Union[Literal['return_collected', 'returning'], str]] = None
    """order delivery status 訂單退貨狀態"""
    items: Optional[List[ReturnOrderItem]] = None
    promotion_items: Optional[List[OrderPromotionItem]] = None
    order: Optional[OrderConfig] = None
    """order data 訂單信息"""
    returned_by: Optional[Any] = None
    """returned by which channel 訂單被退途徑"""
    max_return_total: Optional[Money] = None
    return_order_promotion_items: Optional[List[ReturnOrderPromotionItem]] = None
    applied_user_credits: Optional[Money] = None
    applied_member_point_redeem_to_cash: Optional[Money] = None
    applied_member_point: Optional[int] = None
    """applied member point (After return_order_revamp feature key on)<br/> 分攤的折抵會員點數 (啟用「return_order_revamp」功能後)"""
    custom_discount_items: Optional[List[ReturnOrderItem]] = None
    custom_discount: Optional[Money] = None
    ref_data: Optional[ReturnOrderRefData] = None