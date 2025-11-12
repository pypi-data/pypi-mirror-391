from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.create_channel_price_body import CreateChannelPriceBody as Body
from shopline_sdk.models.price_set import PriceSet

async def call(
    session: aiohttp.ClientSession, channel_id: str, id: str, body: Optional[Body] = None
) -> PriceSet:
    """
    Create Product Channel Price
    
    To create new product channel price
    創建商品分店價格
    
    Path: POST /channels/{channel_id}/products/{id}/prices
    """
    # 构建请求 URL
    url = f"channels/{channel_id}/products/{id}/prices"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.post(
        url, json=json_data, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return PriceSet(**response_data)