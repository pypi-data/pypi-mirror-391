from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

class Response(BaseModel):
    """响应体模型"""
    result: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, metafield_definition_id: str
) -> Response:
    """
    Delete specific metafield
    
    To delete information of metafield definition attached to products
    
    Path: DELETE /metafield_definitions/products/{metafield_definition_id}
    """
    # 构建请求 URL
    url = f"metafield_definitions/products/{metafield_definition_id}"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.delete(
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
        return Response(**response_data)