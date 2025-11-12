from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    tags: List[str]
    """Product tags array 
       商品標簽array"""

class Response(BaseModel):
    """响应体模型"""
    tags: Optional[List[str]] = None

async def call(
    session: aiohttp.ClientSession, productId: str, body: Optional[Body] = None
) -> Response:
    """
    Update (replace) current product tags
    
    Replaces current product tags with input tags array. 
     Each tag mush have at least 3 characters and at most 40 characters.
     When update with invalid length of tags, the update will fail and the respond will be 422.
     以新的標簽取代現有的商品標簽。
     每一個商品標籤必須有最少3個字完及最多40個字完。
     若需更新的商品標籤其中之一不符字完長度規範，更新不會成功及將回傳狀態碼422。
    
    Path: PUT /products/{productId}/tags
    """
    # 构建请求 URL
    url = f"products/{productId}/tags"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.put(
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
            if response.status == 500:
                error = ServerError(**error_data)
                raise ShoplineAPIError(
                    status_code=500,
                    error=error
                )
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)