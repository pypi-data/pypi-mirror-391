from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError


class ItemsItemSchema(BaseModel):
    """Item model for items"""
    id: Optional[str] = None

class Body(BaseModel):
    """请求体模型"""
    items: Optional[List[ItemsItemSchema]] = None

class Response(BaseModel):
    """响应体模型"""
    code: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, id: str, body: Body
) -> Response:
    """
    Bulk Delete Cart Items
    
    Bulk delete cart items.
     刪除購物車商品
    
    Path: DELETE /carts/{id}/items
    """
    # 构建请求 URL
    url = f"carts/{id}/items"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.delete(
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