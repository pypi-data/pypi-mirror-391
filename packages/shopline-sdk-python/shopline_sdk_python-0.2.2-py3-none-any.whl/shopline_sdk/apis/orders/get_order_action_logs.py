from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.order_action_logs import OrderActionLogs
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

async def call(
    session: aiohttp.ClientSession, id: str
) -> OrderActionLogs:
    """
    Get order action logs
    
    To get order action logs with order ID.
     取得訂單活動紀錄。
     Return empty array if order not found.
     如果找不到訂單紀錄，返回empty array。
    
    
    Path: GET /orders/{id}/action_logs
    """
    # 构建请求 URL
    url = f"orders/{id}/action_logs"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, headers=headers
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
        return OrderActionLogs(**response_data)