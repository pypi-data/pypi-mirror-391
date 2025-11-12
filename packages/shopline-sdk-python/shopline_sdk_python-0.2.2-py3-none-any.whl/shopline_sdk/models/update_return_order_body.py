"""Shopline API 数据模型 - UpdateReturnOrderBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .return_order import ReturnOrder


class UpdateReturnOrderBody(BaseModel):
    """Payload for update return order"""
    status: Optional[Union[Literal['confirmed', 'completed', 'cancelled'], str]] = None
    user_credit_expired_at: Optional[str] = None
    """Credit expiry date, a null value means never expired   (After return_order_revamp feature key on)  購物金到期日期, null 表示不會到期 (啟用「return_order_revamp」功能後)"""
    member_point_expired_at: Optional[str] = None
    """Member point expiry date, a null value means never expired<br/> (After return_order_revamp feature key on)<br/> 會員點數到期日期, null 表示不會到期 (啟用「return_order_revamp」功能後)"""