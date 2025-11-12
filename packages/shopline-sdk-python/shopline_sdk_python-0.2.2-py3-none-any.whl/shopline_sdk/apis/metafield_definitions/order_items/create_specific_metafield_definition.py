from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.create_metafield_definition_body import CreateMetafieldDefinitionBody as Body
from shopline_sdk.models.metafield_definition import MetafieldDefinition

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> MetafieldDefinition:
    """
    Create specific metafield definition
    
    To create metafield definition attached to current order items
    
    Path: POST /metafield_definitions/order_items
    """
    # 构建请求 URL
    url = "metafield_definitions/order_items"

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
        return MetafieldDefinition(**response_data)