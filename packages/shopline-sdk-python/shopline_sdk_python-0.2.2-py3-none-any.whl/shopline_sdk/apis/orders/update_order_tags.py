from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.taggable import Taggable
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    tags: Optional[Taggable] = None

class Response(BaseModel):
    """响应体模型"""
    tags: Optional[Taggable] = None

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> Response:
    """
    Update order tags
    
    To update order tags with order IDs.
     Each tag mush have at least 3 characters and at most 40 characters.
     Each order can have at most 10 order tags.
     The maximum of order tags in one store is 100.
     When update with invalid length of tags, the update will fail and the respond will be 422.
     When the amount of order tags exceed 10 or the amount of order tags plus
     the amount of order tags in one store exceeds 100,
     the update will fail and return the current valid tags of that order with status code 200.
     使用訂單ID更新訂單標籤。
     每一個訂單標籤必須有最少3個字完及最多40個字完。
     每一張訂單最多只能有10個訂單標籤。
     每一名店家最多只能有100個訂單標籤。
     若需更新的訂單標籤其中之一不符字完長度規範，更新不會成功及將回傳狀態碼422。 若需更新的訂單標籤超過10個時，又或需更新的訂單標籤加上店家已存在的訂單標籤數量超過100個時，
     更新將不會成功，且仍會回傳狀態碼200及當前訂單的有效訂單標籤。
    
    
    Path: PUT /orders/{id}/tags
    """
    # 构建请求 URL
    url = f"orders/{id}/tags"

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
            if response.status == 404:
                error = NotFoundError(**error_data)
                raise ShoplineAPIError(
                    status_code=404,
                    error=error
                )
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