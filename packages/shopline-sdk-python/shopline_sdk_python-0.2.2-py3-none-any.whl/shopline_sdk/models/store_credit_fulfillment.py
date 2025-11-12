"""Shopline API 数据模型 - StoreCreditFulfillment"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money



class Never_Expire_ItemConfig(BaseModel):
    """Configuration model for never_expire_item"""
    total_value: Optional[float] = None
    """The total value of never expire store credits.<br/> 永久有效的購物金加總"""
    total_value_dollar: Optional[Money] = None
    expire_at: Optional[str] = None
    """This field will be null because the store credit never expire.<br/> 購物金為永久有效，此欄位為 null"""

class StoreCreditFulfillment(BaseModel):
    limit: Optional[float] = None
    """To limit how many items will be returned<br/>限制 items 回傳多少筆資料"""
    remaining_value: Optional[Dict[str, Any]] = None
    """To return the total remaining value of store credit if items count is larger than the limit.<br/> 如果 items 的筆數大於限制，則剩餘未顯示於 items 的點數會加總顯示於此，expire_at 會顯示較快過期的日期"""
    items: Optional[List[Any]] = None
    """The list of store credit fulfillments which will expire in specific date.<br/> 含有到期日的購物金列表，最多顯示 limit 參數個數，剩餘會加總並顯示於 remaining_value"""
    never_expire_item: Optional[Never_Expire_ItemConfig] = None