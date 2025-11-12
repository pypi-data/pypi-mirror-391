from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.delivery_option import DeliveryOption

async def call(
    session: aiohttp.ClientSession, id: str
) -> DeliveryOption:
    """
    Get Delivery Option
    
    To get delivery option information by inputing delivery option ID
    輸入送貨方式ID取得該送貨方式資訊
    
    Path: GET /delivery_options/{id}
    """
    # 构建请求 URL
    url = f"delivery_options/{id}"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return DeliveryOption(**response_data)