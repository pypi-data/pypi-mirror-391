"""Shopline API 数据模型 - AffiliateCampaigns"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .affiliate_campaign import AffiliateCampaign
from .paginatable import Paginatable
from .server_error import ServerError


class AffiliateCampaigns(BaseModel):
    pagination: Optional[Paginatable] = None
    items: Optional[List[AffiliateCampaign]] = None
    proxy_service_error: Optional[ServerError] = None
    last_id: Optional[str] = None
    """Last ID of result. (only for cursor base) 最後一筆 ID(適用於使用遊標取值時)"""
    limit: Optional[int] = None
    """Numbers of result(only for cursor base) 回傳結果的筆數(適用於使用遊標取值時)"""