from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.flash_price_campaigns import FlashPriceCampaigns

class Params(BaseModel):
    """查询参数模型"""
    filter_action: Optional[Union[Literal['overlap'], str]] = None
    """Specify the filter action for flash price campaigns by the start time or/and end time
       指定商品限時促銷價活動的過濾動作，此動作依據start_at或/及end_at進行過濾"""
    start_at: Optional[str] = None
    """Filter those flash price campaigns after specified start_at time.
       取得大於指定start_at時間的商品限時促銷價活動
       *Should use UTC time
       *應使用UTC時間"""
    end_at: Optional[str] = None
    """Filter those flash price campaigns before specified end_at time.
       取得小於指定end_at時間的商品限時促銷價活動
       *Should use UTC time
       *應使用UTC時間"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    per_page: Optional[int] = None
    """Numbers of Orders per Page
      每頁顯示 n 筆資料"""

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> FlashPriceCampaigns:
    """
    Get Flash Price Campaigns
    
    To retrieve flash price campaign list
    獲取商品限時促銷價活動列表
    
    Path: GET /flash_price_campaigns
    """
    # 构建请求 URL
    url = "flash_price_campaigns"

    # 构建查询参数
    query_params = {}
    if params:
        params_dict = params.model_dump(exclude_none=True, by_alias=True)
        for key, value in params_dict.items():
            if value is not None:
                query_params[key] = value

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, params=query_params, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return FlashPriceCampaigns(**response_data)