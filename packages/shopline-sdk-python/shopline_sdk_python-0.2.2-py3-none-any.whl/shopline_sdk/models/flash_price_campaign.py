"""Shopline API 数据模型 - FlashPriceCampaign"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .product import Product
from .translatable import Translatable



class Price_SetsItem(BaseModel):
    """Item model for price_sets"""
    id: Optional[str] = None
    """The id of the price set 商品價格組的ID"""
    price: Optional[Money] = None
    price_sale: Optional[Money] = None
    product: Optional[Dict[str, Any]] = None
    """The product that applied this price set 商品限時促銷價活動的商品"""
    price_details: Optional[List[Dict[str, Any]]] = None
    """The price sets of the variations of the product of this event 商品限時促銷價活動的商品規格價錢組"""

class FlashPriceCampaign(BaseModel):
    id: Optional[str] = None
    """Flash price campaign‘s ID 商品限時促銷價活動ID"""
    title: Optional[str] = None
    """Flash price campaign's title 商品限時促銷價活動名稱"""
    start_at: Optional[str] = None
    """The start time of the event 商品限時促銷價活動開始時間"""
    end_at: Optional[str] = None
    """The end time of the event 商品限時促銷價活動結束時間"""
    merchant_id: Optional[str] = None
    """Merchant ID 商户ID"""
    product_ids: Optional[List[str]] = None
    """The ids of the products which will be presented in this flash price campaign  是次商品限時促銷價活動所包括的商品id"""
    price_sets: Optional[List[Price_SetsItem]] = None
    """The product price sets of this flash price campaigns.  商品限時促銷價活動的商品限時價格。  Presented in GET/flash_price_campaigns{id}, POST/flash_price_campaigns, PUT/flash_price_campaigns{id} but not in GET/flash_price_campaigns.  會於 GET/flash_price_campaigns{id}及POST/flash_price_campaigns及 PUT/flash_price_campaigns{id}出現， 但不於 POST/flash_price_campaigns出現。"""