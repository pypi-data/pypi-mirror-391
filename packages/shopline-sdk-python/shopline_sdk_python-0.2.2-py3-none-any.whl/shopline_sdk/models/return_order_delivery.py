"""Shopline API 数据模型 - ReturnOrderDelivery"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Name_TranslationsConfig(BaseModel):
    """Configuration model for name_translations"""
    en: Optional[str] = None
    zh_hant: Optional[str] = Field(default=None, alias="zh-hant")

class ReturnOrderDelivery(BaseModel):
    id: Optional[str] = None
    """Order Delivery ID"""
    platform: Optional[str] = None
    """Delivery platform 送貨方式類別"""
    status: Optional[Union[Literal['pending', 'shipping', 'shipped', 'arrived', 'collected', 'returned', 'returning'], str]] = None
    """Delivery Status 送貨狀態   Status allows:  pending 備貨中  shipping 發貨中  shipped 已發貨  arrived 已到達  collected 已取貨  returned 已退貨  * returning 退貨中"""
    delivery_status: Optional[Union[Literal['arrived', 'collected', 'expired', 'failed', 'pending', 'request_accepted', 'request_authorized', 'request_submitted', 'returned', 'returning', 'returning_store_closed', 'shipped', 'store_closed'], str]] = None
    """Logistic Service Order Status 配送狀態   Status allows:  arrived 已到達  collected 已取貨  expired 已過出貨期限  failed 失敗  pending 未執行  request_accepted 可供出貨  request_authorized 待處理  request_submitted 處理中  returned 已退貨  returning 退貨中  returning_store_closed 退貨門市關轉  shipped 已出貨  * store_closed 門市關閉"""
    delivery_option_id: Optional[str] = None
    """Delivery Option ID 送貨選項ID"""
    name_translations: Optional[Name_TranslationsConfig] = None
    """Delivery Option Name Translations 送貨選項名稱翻譯"""