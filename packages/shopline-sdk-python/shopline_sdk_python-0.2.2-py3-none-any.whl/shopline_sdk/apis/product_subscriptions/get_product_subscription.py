from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.product_subscription import ProductSubscription

async def call(
    session: aiohttp.ClientSession, id: str
) -> ProductSubscription:
    """
    Get Product Subscription
    
    To get detailed information for a specific product subscription with its ID
     使用定期購ID獲取特定一個定期購的詳細資料
    
    Path: GET /product_subscriptions/{id}
    """
    # 构建请求 URL
    url = f"product_subscriptions/{id}"

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
        return ProductSubscription(**response_data)