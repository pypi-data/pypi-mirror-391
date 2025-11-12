from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.custom_field import CustomField

async def call(
    session: aiohttp.ClientSession
) -> List[CustomField]:
    """
    Get Custom Fields
    
    To get custom fields within customer data.
    獲取顧客自訂欄位
    
    Path: GET /custom_fields
    """
    # 构建请求 URL
    url = "custom_fields"

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
        return [CustomField(**item) for item in response_data]