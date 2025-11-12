from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.flash_price_campaign import FlashPriceCampaign

async def call(
    session: aiohttp.ClientSession, id: str
) -> FlashPriceCampaign:
    """
    Get a Flash Price Campaign
    
    To retrieve a flash price campaign with its id
    獲取商品限時促銷價活動
    
    Path: GET /flash_price_campaigns/{id}
    """
    # 构建请求 URL
    url = f"flash_price_campaigns/{id}"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return FlashPriceCampaign(**response_data)