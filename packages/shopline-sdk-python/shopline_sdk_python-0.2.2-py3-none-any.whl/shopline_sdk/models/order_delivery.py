"""Shopline API 数据模型 - OrderDelivery"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class OrderDelivery(BaseModel):
    id: Optional[str] = None
    """Order Delivery ID 訂單配送ID"""
    delivery_option_id: Optional[str] = None
    """Delivery Option ID 送貨方式ID"""
    platform: Optional[str] = None
    """Delivery platform 送貨方式類別"""
    status: Optional[Union[Literal['pending', 'shipping', 'shipped', 'arrived', 'collected', 'returned', 'returning'], str]] = None
    """Delivery Status 送貨狀態   Status allows:  pending 備貨中  shipping 發貨中  shipped 已發貨  arrived 已到達  collected 已取貨  returned 已退貨  * returning 退貨中"""
    delivery_status: Optional[Union[Literal['arrived', 'collected', 'expired', 'failed', 'pending', 'request_accepted', 'request_authorized', 'request_submitted', 'returned', 'returning', 'returning_store_closed', 'shipped', 'store_closed'], str]] = None
    """Logistic Service Order Status 配送狀態   Status allows:  arrived 已到達  collected 已取貨  expired 已過出貨期限  failed 失敗  pending 未執行  request_accepted 可供出貨  request_authorized 待處理  request_submitted 處理中  returned 已退貨  returning 退貨中  returning_store_closed 退貨門市關轉  shipped 已出貨  * store_closed 門市關閉"""
    name_translations: Optional[Translatable] = None
    total: Optional[Translatable] = None
    shipped_at: Optional[str] = None
    """Shipped Time 已送貨時間 (UTC +0)"""
    arrived_at: Optional[str] = None
    """Arrived Time 已到達時間 (UTC +0)"""
    collected_at: Optional[str] = None
    """Collected Time 已取貨時間 (UTC +0)"""
    returned_at: Optional[str] = None
    """Returned Time 已退貨時間 (UTC +0)"""
    updated_at: Optional[str] = None
    """Updated Time 更新時間 (UTC +0)"""
    remark: Optional[str] = None
    """Order remark 訂單出貨備註"""
    request_accepted_at: Optional[str] = None
    """Logistic accepted shipment time 物流商收到出貨時間"""
    request_authorized_at: Optional[str] = None
    """Logistic authorized shipment time 物流商接受出貨時間"""
    request_submitted_at: Optional[str] = None
    """Logistic proceeded shipment time 物流商處理出貨時間"""
    requested_fmt_at: Optional[str] = None
    """Shipment execution time (Family Mart) 執行出貨時間 (全家)"""
    return_order_id: Optional[str] = None
    """Return order ID 退貨訂單編號"""
    store_closed_at: Optional[str] = None
    """Pick up store closed time 訂單取貨門市關轉時間"""
    require_expired_upload: Optional[bool] = None
    """Check if delivery needs reupload and schedule aggregation upload"""
    require_storeclosed_upload: Optional[bool] = None
    """whether scheduled upload to 7-11 B2C FTP, SUP"""
    storeclosed_upload_at: Optional[str] = None
    """prevent duplicated update storeclosed (EIN.36) for 7-11 B2C"""
    exp_type: Optional[str] = None
    """exp type"""
    requires_customer_address: Optional[bool] = None
    """Whether the customer address is required 是否需要顧客提供地址"""