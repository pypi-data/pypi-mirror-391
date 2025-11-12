from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.gift import Gift
from shopline_sdk.models.translatable import Translatable

class Body(BaseModel):
    """请求体模型"""
    title_translations: Optional[Translatable] = None
    unlimited_quantity: Optional[bool] = None
    sku: Optional[str] = None
    weight: Optional[float] = None
    cost: Optional[Translatable] = None
    quantity: Optional[float] = None
    media_ids: Optional[List[str]] = None
    product_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> Gift:
    """
    Create Gift
    
    To create gift
    建立贈品
    
    Path: POST /gifts
    """
    # 构建请求 URL
    url = "gifts"

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
        return Gift(**response_data)