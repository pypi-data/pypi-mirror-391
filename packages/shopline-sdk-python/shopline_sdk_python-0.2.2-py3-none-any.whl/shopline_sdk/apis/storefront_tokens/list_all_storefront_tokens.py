from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.storefront_token import StorefrontToken

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[StorefrontToken]] = None

async def call(
    session: aiohttp.ClientSession
) -> Response:
    """
    List all storefront tokens
    
    List all storefront tokens
    列出所有店面令牌
    
    Path: GET /storefront_tokens
    """
    # 构建请求 URL
    url = "storefront_tokens"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)