"""Shopline API 数据模型 - OrderInspectItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class OrderInspectItem(BaseModel):
    quantity: Optional[int] = None
    """Order inspect item quantity  驗貨商品數量"""
    inspect_status: Optional[Union[Literal['accepted', 'rejected', 'pending'], str]] = None
    """Order inspect item status"""
    return_reason_key: Optional[Union[Literal['not_expected', 'broke_during_delivery', 'wrong_variation', 'wrong_item', 'other', 'admin_return_order'], str]] = None
    """return reason 退貨原因"""
    return_remark: Optional[str] = None
    """return reason remark when the customer return reason is other   退貨原因備註，如果退貨原因不是 other 則為 null"""
    inspect_remark: Optional[str] = None
    """inspect remark  檢驗備註"""