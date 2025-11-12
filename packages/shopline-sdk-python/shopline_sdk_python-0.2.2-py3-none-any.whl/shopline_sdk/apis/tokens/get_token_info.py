from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

class Response(BaseModel):
    """响应体模型"""
    staff: Optional[Dict[str, Any]] = None
    merchant: Optional[Dict[str, Any]] = None

async def call(
    session: aiohttp.ClientSession
) -> Response:
    """
    Get Token Info
    
    Retrieve information of the access token
    抓取access token的信息
    
    Path: GET /token/info
    """
    # 构建请求 URL
    url = "token/info"

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