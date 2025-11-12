"""Shopline API 数据模型 - FlashPriceCampaigns"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .flash_price_campaign import FlashPriceCampaign
from .paginatable import Paginatable


class FlashPriceCampaigns(BaseModel):
    items: Optional[List[FlashPriceCampaign]] = None
    pagination: Optional[Paginatable] = None
    not_terminated_campaigns_count: Optional[float] = None
    """The number of active campaigns  未過期的商品限時促銷價活動的數量"""