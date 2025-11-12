from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Response(BaseModel):
    """响应体模型"""
    delivery_status: Optional[Union[Literal['request_accepted', 'request_authorized', 'request_submitted'], str]] = None
    tracking_number: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, id: str
) -> Response:
    """
    Execute Shipment
    
    Execute shipment, currently we support order with following delivery service: 7-11 B2C/7-11 C2C/FMT B2C/FMT C2C/T-cat/SF/HCT 
     Only applicable to order in pending delivery status.
    
    Path: PATCH /orders/{id}/execute_shipment
    """
    # 构建请求 URL
    url = f"orders/{id}/execute_shipment"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.patch(
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
        return Response(**response_data)