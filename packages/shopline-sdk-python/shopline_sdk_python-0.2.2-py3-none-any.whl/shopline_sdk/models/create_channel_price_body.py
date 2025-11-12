"""Shopline API 数据模型 - CreateChannelPriceBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Price_DetailsItem(BaseModel):
    """Item model for price_details"""
    variation_key: str
    """The id of the variation product 商品規格ID"""
    price: float
    """The price of the product when the event is started  商品規格分店價格"""

class CreateChannelPriceBody(BaseModel):
    """Payload for creating product channel price"""
    price: Optional[float] = None
    """The Channel price of the product 商品分店價格"""
    price_details: Optional[List[Price_DetailsItem]] = None
    """The channel price sets of the variations of the product  商品規格分店價格"""