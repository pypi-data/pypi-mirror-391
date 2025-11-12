"""Shopline API 数据模型 - CreateFlashPriceCampaignBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Flash_Price_CampaignConfig(BaseModel):
    """Configuration model for flash_price_campaign"""
    start_at: str
    """The start time of the event 商品限時促銷價活動的開始時間  *Should use UTC time  *應使用UTC時間"""
    end_at: str
    """The end time of the event 商品限時促銷價活動的結束時間  *Should use UTC time  *應使用UTC時間"""
    title: str
    """Flash price campaign's title 商品限時促銷價活動的名稱"""
    price_sets: Optional[List[Dict[str, Any]]] = None
    """The product price sets of this flash price campaigns.  商品限時促銷價活動的商品限時價格。"""

class CreateFlashPriceCampaignBody(BaseModel):
    """Payload for creating flash price campaign"""
    flash_price_campaign: Optional[Flash_Price_CampaignConfig] = None