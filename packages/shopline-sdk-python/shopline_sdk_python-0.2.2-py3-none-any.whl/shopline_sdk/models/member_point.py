"""Shopline API 数据模型 - MemberPoint"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class MemberPoint(BaseModel):
    customer_id: Optional[str] = None
    """Customer ID"""
    point_balance: Optional[int] = None
    """Member Point 現有點數"""
    remarks: Optional[str] = None
    """Point Change Reason 點數更動原因"""
    value: Optional[int] = None
    """Point 點數"""
    order_id: Optional[str] = None
    """Order ID"""
    order_number: Optional[str] = None
    """Order Number"""
    type: Optional[Union[Literal['manual', 'auto_reward', 'expired', 'order_redeemed', 'redeemed_to_cash', 'order_split_revert', 'product_review_reward', 'member_info_reward', 'return_order_revert', 'order_edit_revert'], str]] = None
    """Member point type 點數種類  ----  manual: 手動增減點數（店家手動發送、取消訂單/退貨訂單回補）  auto_reward: 點數回饋  expired: 點數過期  order_redeemed: 使用點數兌換贈品於訂單  redeemed_to_cash: 使用點數折現於訂單  order_split_revert: 回補點數（來自拆單）  product_review_reward: 商品評價獎賞  member_info_reward: 會員資料獎賞  return_order_revert: 退貨單回補會員點數  order_edit_revert: 訂單編輯回補會員點數"""
    is_redeem: Optional[bool] = None
    """Redeemed? 已兌換?"""
    expire_at: Optional[str] = None
    """Expiry date, a null value means never expired 到期日期, null 表示不會到期"""
    created_at: Optional[str] = None
    """Created Time 點數創建時間"""