from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.order import Order
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError


class OrderItemsItemSchema(BaseModel):
    """Item model for order_items"""
    id: str
    quantity: float

class Body(BaseModel):
    """请求体模型"""
    order_items: List[OrderItemsItemSchema]
    """The order_items of the order would like to be split to a new order.
       想要拆單的訂單項目"""
    updated_at: str
    """The updated_at of the order would like to be split.
       欲被拆單的訂單更新時間
       * Should use UTC time"""
    send_child_email: Optional[bool] = None
    """Do you want to notify the customer that the child order already created by email?
       是否發送拆單成立通知（新訂單）給顧客"""
    send_parent_email: Optional[bool] = None
    """Do you want to notify the customer that the parent order already split by email?
       是否發送拆單成立通知（原訂單）給顧客"""

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> Order:
    """
    Split Order
    
    To split an order with open API
    透過 open API 進行拆單
    
    Path: POST /orders/{id}/split
    """
    # 构建请求 URL
    url = f"orders/{id}/split"

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
        return Order(**response_data)