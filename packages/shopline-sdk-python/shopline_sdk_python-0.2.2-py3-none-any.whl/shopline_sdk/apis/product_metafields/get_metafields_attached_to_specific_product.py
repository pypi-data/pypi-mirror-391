from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.metafield_value import MetafieldValue

class Params(BaseModel):
    """查询参数模型"""
    filters: Optional[List[str]] = Field(default=None, alias="filters[]")
    """Search criteria
       In format of {namespace}.{key}:{value}
       {namespace} - required
       {key} - required
       {value} - optional"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[MetafieldValue]] = None

async def call(
    session: aiohttp.ClientSession, product_id: str, params: Optional[Params] = None
) -> Response:
    """
    Get metafields attached to specific product
    
    To get information of metafield attached to specific product
    
    Path: GET /products/{product_id}/metafields
    """
    # 构建请求 URL
    url = f"products/{product_id}/metafields"

    # 构建查询参数
    query_params = {}
    if params:
        params_dict = params.model_dump(exclude_none=True, by_alias=True)
        for key, value in params_dict.items():
            if value is not None:
                query_params[key] = value

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, params=query_params, headers=headers
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