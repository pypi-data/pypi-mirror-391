"""Shopline API 数据模型 - OrderPromotionItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money


class OrderPromotionItem(BaseModel):
    id: Optional[str] = None
    """Order item's ID (ID of an order item's collection, including item_type, item_id..and so on)  系統自行創建訂單折扣ID"""
    discountable_amount: Optional[Any] = None
    discounted_amount: Optional[Money] = None
    subtotal_after: Optional[Money] = None
    promotion_data: Optional[Dict[str, Any]] = None
    """Promotion Data 促銷資訊"""
    coupon_code: Optional[str] = None
    """Promotion coupon code 促銷優惠代碼"""
    updated_at: Optional[str] = None
    """Promotion Updated Time 此產品使用促銷更新時間"""
    created_at: Optional[str] = None
    """Promotion Created Time 此產品使用促銷創造時間（通常與產品創造時間一致）"""