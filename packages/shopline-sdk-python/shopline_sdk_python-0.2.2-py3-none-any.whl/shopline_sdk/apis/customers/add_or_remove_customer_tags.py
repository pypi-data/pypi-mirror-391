from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.taggable import Taggable
from shopline_sdk.models.unauthorized_error import UnauthorizedError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    tags: Taggable
    update_mode: Union[Literal['add', 'remove'], str]
    """Update Mode
      更新模式"""

class Response(BaseModel):
    """响应体模型"""
    tags: Optional[Taggable] = None

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> Response:
    """
    Add or remove customer tags
    
    To add or remove customer tags with customer IDs.
     Each tag mush have at least 3 characters and at most 40 characters.
     When removing tags, there is no character length limit.
     Each customer can have at most 60 customer tags.
     When update with invalid length of tags, the update will fail and the respond will be 422.
     When the amount of customer tags exceed 60,
     the update will fail and return the current valid tags of that customer with status code 200.
     使用顧客ID添加或移除顧客標籤。
     每一個顧客標籤必須有最少3個字完及最多40個字完。
     當移除標籤時，字元長度沒有限制。
     每一個顧客最多只能有60個顧客標籤。
     若需更新的顧客標籤其中之一不符字完長度規範，更新不會成功及將回傳狀態碼422。 若需更新的顧客標籤超過60個時，
     更新將不會成功，且仍會回傳狀態碼200及當前顧客的有效顧客標籤。
    
    
    Path: PATCH /customers/{id}/tags
    """
    # 构建请求 URL
    url = f"customers/{id}/tags"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.patch(
        url, json=json_data, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            if response.status == 401:
                error = UnauthorizedError(**error_data)
                raise ShoplineAPIError(
                    status_code=401,
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