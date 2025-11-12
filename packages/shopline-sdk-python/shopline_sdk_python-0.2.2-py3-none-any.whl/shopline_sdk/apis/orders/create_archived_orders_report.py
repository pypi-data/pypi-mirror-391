from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError


class FiltersSchema(BaseModel):
    """Model for filters"""
    start_date: Optional[str] = None
    """Start time to filter archived orders.
       匯出冷區報表開始時間"""
    end_date: Optional[str] = None
    """End time to filter archived orders.
       匯出冷區報表結束時間"""

class Body(BaseModel):
    """请求体模型"""
    filters: Optional[FiltersSchema] = None
    callback_url: Optional[str] = None
    """merchant's callback url
      店家提供 callback url"""

class Response(BaseModel):
    """响应体模型"""
    message: Optional[List[Any]] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> Response:
    """
    Create Archived Orders Report
    
    Create Archived Orders Report
    查詢冷區訂單資料
    
    Path: POST /orders/archived_orders
    """
    # 构建请求 URL
    url = "orders/archived_orders"

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