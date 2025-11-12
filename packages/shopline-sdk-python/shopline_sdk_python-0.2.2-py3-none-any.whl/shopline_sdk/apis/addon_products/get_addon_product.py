from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.addon_product import AddonProduct

async def call(
    session: aiohttp.ClientSession, id: str
) -> AddonProduct:
    """
    Get Addon Product
    
    To get detailed information for a specific addon product with its ID
    使用加購品ID獲取特定一個商品的詳細資料
    
    Path: GET /addon_products/{id}
    """
    # 构建请求 URL
    url = f"addon_products/{id}"

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
        return AddonProduct(**response_data)