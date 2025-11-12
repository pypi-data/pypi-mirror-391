from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.limit_exceeded_error import LimitExceededError
from shopline_sdk.models.storefront_token import StorefrontToken
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    backend_token: Optional[bool] = None
    """Indicate if it is a backend token for different setup such as ratelimit"""

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> StorefrontToken:
    """
    Create storefront token
    
    Create storefront token
    創建一個新的店面令牌
    
    Path: POST /storefront_tokens
    """
    # 构建请求 URL
    url = "storefront_tokens"

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
            if response.status == 422:
                error = UnprocessableEntityError(**error_data)
                raise ShoplineAPIError(
                    status_code=422,
                    error=error
                )
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return StorefrontToken(**response_data)