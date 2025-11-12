from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError


class CancelledReasonSchema(BaseModel):
    """Model for cancelled_reason"""
    key: Optional[str] = None
    message: Optional[str] = None


class RevertCreditsSchema(BaseModel):
    """revert credits information
    回補購物金資訊"""
    strategy: Optional[Union[Literal['none', 'revert'], str]] = None
    """determine revert credits or not, default do not revert
      是否回補購物金，預設不回補"""


class RevertMemberPointsSchema(BaseModel):
    """revert member points information
    回補點數資訊"""
    strategy: Optional[Union[Literal['none', 'revert'], str]] = None
    """determine revert member points or not, default do not revert
      是否回補點數，預設不回補"""

class Body(BaseModel):
    """请求体模型"""
    cancelled_reason: Optional[CancelledReasonSchema] = None
    revert_credits: Optional[RevertCreditsSchema] = None
    """revert credits information
      回補購物金資訊"""
    revert_member_points: Optional[RevertMemberPointsSchema] = None
    """revert member points information
      回補點數資訊"""
    operated_by: Optional[Union[Literal['merchant', 'customer'], str]] = None
    """where to cancel the order, the default is customer
      從哪裡取消訂單，預設是 customer"""
    refund_order: Optional[bool] = None
    """Do you want to refund the order? 
      是否要退款此筆訂單
      -
      *Default:true"""
    mail_notify: Optional[bool] = None
    """Do you want to notify the customer via email when the order is cancelled? 
      此筆訂單取消之後是否要通知顧客？
      -
      *Default:true"""

class Response(BaseModel):
    """响应体模型"""
    order_items_stock_tag: Optional[List[Dict[str, Any]]] = None

async def call(
    session: aiohttp.ClientSession, orderId: str, body: Optional[Body] = None
) -> Response:
    """
    Cancel Order
    
    To cancel order
    取消訂單
    
    Path: PATCH /orders/{orderId}/cancel
    """
    # 构建请求 URL
    url = f"orders/{orderId}/cancel"

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
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)