from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    sub: Optional[str] = None
    """New identifier mapping for customer, allow regex ^[a-zA-Z0-9.\-@+ _]+$"""

class Response(BaseModel):
    """响应体模型"""
    message: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, customer_id: str, body: Optional[Body] = None
) -> Response:
    """
    Update multipass linking for customer
    
    Update customer's active linking record used for multipass login
    
    Path: POST /multipass/customers/{customer_id}/linkings
    """
    # 构建请求 URL
    url = f"multipass/customers/{customer_id}/linkings"

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
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)