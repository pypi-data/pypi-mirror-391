from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.storefront_o_auth_application import StorefrontOAuthApplication

class Body(BaseModel):
    """请求体模型"""
    name: Optional[str] = None
    redirect_uri: Optional[str] = None
    is_redirect_to_simplified_login: Optional[bool] = None
    """If the app will redirect to simplified login"""

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> StorefrontOAuthApplication:
    """
    Create Storefront OAuth Application
    
    
    
    Path: POST /storefront/oauth_applications
    """
    # 构建请求 URL
    url = "storefront/oauth_applications"

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
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return StorefrontOAuthApplication(**response_data)