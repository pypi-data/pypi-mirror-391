"""Shopline API 数据模型 - UpdateFlashPriceCampaignBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class ProductConfig(BaseModel):
    """Configuration model for product"""
    start_at: str
    """The start time of the event 商品限時促銷價活動的開始時間  *Should use UTC time  *應使用UTC時間"""
    end_at: str
    """The end time of the event 商品限時促銷價活動的結束時間  *Should use UTC time  *應使用UTC時間"""
    title: str
    """Flash price campaign's title 商品限時促銷價活動的名稱"""
    price_sets: Optional[List[Dict[str, Any]]] = None
    """The product price sets of this flash price campaigns.  商品限時促銷價活動的商品限時價格。"""

class UpdateFlashPriceCampaignBody(BaseModel):
    """Payload for updating flash price campaign"""
    product: Optional[ProductConfig] = None