from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.order_delivery import OrderDelivery

class Body(BaseModel):
    """请求体模型"""
    remark: Optional[str] = None
    """Delivery remark
      出貨備註 Up to 255 words.
      最多只能填寫255個字。"""
    status: Optional[str] = None
    """Order delivery status
      訂單送貨狀態 Order delivery Status only allows
      訂單送貨狀態只可以填入 pending 備貨中
       shipping 發貨中
       shipped 已發貨
       arrived 已到達
       collected 已取貨
       returned 已退貨
       returning 退貨中"""

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> OrderDelivery:
    """
    Update Order Delivery
    
    To update a specific order delivery with its ID
    使用訂單ID配送更新特定一筆訂單配送的資料
    
    Path: PUT /order_deliveries/{id}
    """
    # 构建请求 URL
    url = f"order_deliveries/{id}"

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
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return OrderDelivery(**response_data)