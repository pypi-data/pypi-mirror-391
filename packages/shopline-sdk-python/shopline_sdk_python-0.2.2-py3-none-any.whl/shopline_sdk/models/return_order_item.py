"""Shopline API 数据模型 - ReturnOrderItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .order_inspect_item import OrderInspectItem


class ReturnOrderItem(BaseModel):
    id: Optional[str] = None
    """Order item's ID (ID of an order item's collection, including item_type, item_id..and so on)  系統自行創建訂單品項ID"""
    item_type: Optional[Union[Literal['Product', 'AddonProduct', 'Gift', 'CustomProduct'], str]] = None
    """Order item type: Product  商品  AddonProduct 加購品 Gift 贈品 CustomProduct 自訂商品"""
    item_data: Optional[Dict[str, Any]] = None
    """CartItem snapshot 在第三方合作夥伴下單之前,在購物車內時的資訊快照"""
    object_data: Optional[Dict[str, Any]] = None
    """product snapshot 在第三方合作夥伴下單之前,商品的資訊快照"""
    item_id: Optional[str] = None
    """ID of Product/Addon Product/Gift 商品/加購品/贈品的ID  (Custom Product doesn't have a item_id) (自訂商品沒有item_id)"""
    item_variation_id: Optional[str] = None
    """(To-Be-Deprecated) 規格商品ID請使用下方item_variation_key欄位"""
    item_price: Optional[Money] = None
    item_points: Optional[int] = None
    """Points used for single item 兌換商品所需點數"""
    quantity: Optional[int] = None
    """Order item quantity 商品數量"""
    total: Optional[Money] = None
    total_points: Optional[int] = None
    """Total points cost on same product (item_points * quantity)  此商品的總點數"""
    order_inspect_items: Optional[List[OrderInspectItem]] = None