from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.order_delivery import OrderDelivery

async def call(
    session: aiohttp.ClientSession, id: str
) -> OrderDelivery:
    """
    Get Order Delivery
    
    To get detailed information for a specific order delivery with its ID
    使用訂單ID配送獲取特定一筆訂單配送的詳細資料
    
    Path: GET /order_deliveries/{id}
    """
    # 构建请求 URL
    url = f"order_deliveries/{id}"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, headers=headers
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