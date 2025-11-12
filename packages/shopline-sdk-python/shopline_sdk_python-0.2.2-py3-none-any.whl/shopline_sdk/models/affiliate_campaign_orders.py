"""Shopline API 数据模型 - AffiliateCampaignOrders"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .affiliate_campaign_order import AffiliateCampaignOrder


class AffiliateCampaignOrders(BaseModel):
    items: Optional[List[AffiliateCampaignOrder]] = None
    limit: Optional[int] = None
    """Numbers of Orders"""
    last_id: Optional[str] = None
    """The last ID of the orders"""