from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError

class Body(BaseModel):
    """请求体模型"""
    orderIds: Optional[List[str]] = None

class Response(BaseModel):
    """响应体模型"""
    processingOrderIds: Optional[List[Any]] = None
    processingFailedOrderIds: Optional[List[Any]] = None
    statusErrorOrderIds: Optional[List[Any]] = None
    platformNotSupportOrderIds: Optional[List[Any]] = None
    notFoundOrderIds: Optional[List[Any]] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> Response:
    """
    Bulk Execute Shipment
    
    To bulk update the order delivery status. Note that any update failure will be ignored. 
     批量更新訂單送貨狀態。注意任何更新錯誤會被忽略。 
     We support order with following delivery service: 7-11 Cross Border, FMT Freeze, Tcat.
     目前支援以下物流：7-11 跨境、全家冷凍、黑貓宅配
     * Currently, this endpoint only support updating orders delivery status with same status.
     * 現階段只支持批量更新相同的訂單送貨狀態。
    
    
    Path: PATCH /orders/execute_shipment
    """
    # 构建请求 URL
    url = "orders/execute_shipment"

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