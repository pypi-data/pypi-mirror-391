from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

class Body(BaseModel):
    """请求体模型"""
    product_ids: Optional[List[Any]] = None
    """Product IDs
      商品ID
      (Max: 1000)"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Any]] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> Response:
    """
    Get Locked Inventory Count
    
    Get Locked Inventory Count
    取得直播保留庫存數字
    
    Path: POST /products/locked_inventory_count
    """
    # 构建请求 URL
    url = "products/locked_inventory_count"

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
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)