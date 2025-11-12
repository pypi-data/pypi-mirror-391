"""Shopline API 数据模型 - AffiliateCampaignOrder"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .order_campaign_item import OrderCampaignItem
from .order_delivery import OrderDelivery
from .order_item import OrderItem
from .order_payment import OrderPayment
from .order_promotion_item import OrderPromotionItem
from .utm_data import UtmData


class AffiliateCampaignOrder(BaseModel):
    id: Optional[str] = None
    """Order ID 訂單ID"""
    order_number: Optional[str] = None
    """Order Number 訂單號碼"""
    system_order_number: Optional[str] = None
    """系统生成的訂單號"""
    merchant_order_number: Optional[str] = None
    """店家自定義訂單號 (會根據rollout_key選擇用哪個order_number)"""
    status: Optional[Union[Literal['temp', 'pending', 'removed', 'confirmed', 'completed', 'cancelled'], str]] = None
    """Order Status 訂單狀態  -  Status allows:  temp 暫存狀態  pending 處理中  removed 已刪除  confirmed 已確認  completed 已完成  cancelled 已取消"""
    is_guest_checkout: Optional[bool] = None
    """是否為訪客結帳"""
    order_remarks: Optional[str] = None
    """Order Remarks 訂單備註"""
    order_payment: Optional[OrderPayment] = None
    customer_id: Optional[str] = None
    """Customer ID 顧客ID"""
    customer_name: Optional[str] = None
    """Customer Name 顧客名稱"""
    customer_email: Optional[str] = None
    """Customer Email 顧客 Email"""
    order_delivery: Optional[OrderDelivery] = None
    subtotal: Optional[Money] = None
    order_discount: Optional[Money] = None
    user_credit: Optional[Money] = None
    total_tax_fee: Optional[Money] = None
    total: Optional[Money] = None
    order_points: Optional[int] = None
    """Points used 會員點數使用"""
    order_points_to_cash: Optional[Money] = None
    subtotal_items: Optional[List[OrderItem]] = None
    promotion_items: Optional[List[OrderPromotionItem]] = None
    custom_discount_items: Optional[List[OrderItem]] = None
    ref_order_id: Optional[str] = None
    """For third party custom order id 可供儲存第三方訂單ID"""
    ref_customer_id: Optional[str] = None
    """For third party custom customer id 可供儲存第三方顧客ID"""
    parent_order_id: Optional[str] = None
    """Parent Order ID 拆單後之母訂單ID"""
    child_order_ids: Optional[List[str]] = None
    """Child Order ID 拆單後之子訂單ID"""
    split_at: Optional[str] = None
    """Order Split Time 拆單時間"""
    confirmed_at: Optional[str] = None
    """Order Confirmed Time 訂單確認時間 (如尚未確認則顯示null)"""
    updated_at: Optional[str] = None
    """Order Updated Time 訂單更新時間 *UTC Time"""
    created_at: Optional[str] = None
    """Order Created Time 訂單創造日期 *UTC Time"""
    utm_data: Optional[UtmData] = None
    created_by: Optional[Union[Literal['openapi', 'admin', 'shop', 'shop_crm', 'pos', 'sc', 'mc', 'import'], str]] = None
    """Channel that created the order 建立訂單的渠道"""
    affiliate_campaign: Optional[OrderCampaignItem] = None
    return_adjustment_amount: Optional[Money] = None
    inclusive_tax_info: Optional[Dict[str, Any]] = None
    """inclusive tax information 內含稅信息"""
    checkout_object_number: Optional[str] = None
    """multi checkout object number 多購物車編號"""