from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.metafield_value import MetafieldValue


class ItemsItemSchema(BaseModel):
    """Item model for items"""
    id: Optional[str] = None
    resource_id: Optional[str] = None
    namespace: Optional[str] = None
    key: Optional[str] = None
    field_type: Optional[Union[Literal['single_line_text_field', 'multi_line_text_field', 'number_integer', 'number_decimal', 'json', 'boolean', 'url'], str]] = None
    field_value: Optional[Union[str, float, bool, Dict[str, Any]]] = None

class Body(BaseModel):
    """请求体模型"""
    items: Optional[List[ItemsItemSchema]] = None

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[MetafieldValue]] = None

async def call(
    session: aiohttp.ClientSession, order_id: str, body: Optional[Body] = None
) -> Response:
    """
    bulk update metafield
    
    bulk update information of metafield attached to order items of specific order
    
    Path: PUT /orders/{order_id}/items/metafields/bulk
    """
    # 构建请求 URL
    url = f"orders/{order_id}/items/metafields/bulk"

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
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)