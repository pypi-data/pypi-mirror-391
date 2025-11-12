"""Shopline API 数据模型 - SaleComment"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class SaleComment(BaseModel):
    sale_id: Optional[str] = None
    """Live Room ID 直播間 ID"""
    platform: Optional[str] = None
    """Live Platform 直播渠道"""
    page_id: Optional[str] = None
    """Fan page ID, some channels may not have it. 粉絲專頁 ID, 部分渠道沒有"""
    post_id: Optional[str] = None
    """Post ID, some channels may not have it. 貼文 ID, 部分渠道沒有"""
    post_sales_user_id: Optional[str] = None
    """Customer ID in live stream 直播間顧客 ID"""
    user_name: Optional[str] = None
    """Customer Name 顧客姓名"""
    comment_id: Optional[str] = None
    """Comment ID 留言 ID"""
    content: Optional[str] = None
    """Comment Content 留言內容"""
    hit_keyword: Optional[int] = None
    """Whether it hits the keyword, (only includes product keywords).  是否命中關鍵字(僅包含商品關鍵字)  0: 未命中; 1: 命中"""
    has_add_cart: Optional[int] = None
    """Whether the add-to-cart was successful. 是否加購成功  hit_keyword=1時，此欄位才會有值"""
    product_info: Optional[List[Any]] = None
    """Information about the added-to-cart items. 加購的商品資料  hit_keyword=1時，此欄位才會有值"""