"""Shopline API 数据模型 - PurchaseOrder"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .agent import Agent
from .channel import Channel
from .money import Money
from .purchase_order_item import PurchaseOrderItem
from .supplier import Supplier



class Group_Purchase_OrdersItem(BaseModel):
    """Item model for group_purchase_orders"""
    id: Optional[str] = None
    purchase_number: Optional[str] = None
    status: Optional[Union[Literal['pending', 'received', 'completed', 'cancelled', 'removed'], str]] = None

class PurchaseOrder(BaseModel):
    id: Optional[str] = None
    """Purchase Order ID 進貨單 ID"""
    type: Optional[Union[Literal['purchase', 'return'], str]] = None
    """Type  類型"""
    number: Optional[str] = None
    """PurchaseOrder Number 單號"""
    custom_number: Optional[str] = None
    """Custom Number 自訂單號"""
    status: Optional[Union[Literal['pending', 'received', 'completed', 'cancelled', 'removed'], str]] = None
    """Status 貨單狀態"""
    arrival_status: Optional[Union[Literal['pending_to_receive', 'partial', 'all_received', 'all_returned'], str]] = None
    """Arrival Status 到貨狀態"""
    scheduled_time: Optional[str] = None
    """Time scheduled to arrive at<br預定到貨日期"""
    actual_time: Optional[str] = None
    """Actual Time to arrive at 完成進貨日期"""
    other_fee: Optional[Money] = None
    total_amount: Optional[Money] = None
    current_amount: Optional[Money] = None
    total_quantity: Optional[int] = None
    """Total Quantity 進貨數量"""
    current_quantity: Optional[int] = None
    """Current Quantity 點收數量"""
    note: Optional[str] = None
    """Note 備註"""
    child_id: Optional[str] = None
    """Child ID 子進貨單 ID"""
    group_id: Optional[str] = None
    """Group ID 進貨單群組 ID"""
    items: Optional[List[List[PurchaseOrderItem]]] = None
    issuer: Optional[Agent] = None
    executor: Optional[Agent] = None
    channel: Optional[Channel] = None
    supplier: Optional[Supplier] = None
    has_removed_items: Optional[bool] = None
    """Has Removed Items 有商品被移除的進貨單項目"""
    group_purchase_orders: Optional[List[Group_Purchase_OrdersItem]] = None
    created_at: Optional[str] = None
    """Created at 建立時間"""
    updated_at: Optional[str] = None
    """Updated at 更新時間"""