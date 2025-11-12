from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.product import Product
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    bulk_data: Optional[List[Any]] = None
    """Product, Product Variation's ID and warehouse ID, 
      商品、商品規格、贈品或加購品的商品貨號"""
    is_replace: bool
    """Whether replacing the original quantity
      是否取代原本數量
      
      true: replace the product's quantity with the number you provided
      取代原本數量
      
      false: increase/decrease the quantity with the number you provided
      增加/減少數量"""

class Response(BaseModel):
    """响应体模型"""
    errors: Optional[List[Any]] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> Response:
    """
    Bulk Update Stock
    
    To update the mutiple product's stock with its ID
    使用多個商品 ID 更新商品在各個倉庫的庫存
    
    Path: PUT /products/bulk_update_stocks
    """
    # 构建请求 URL
    url = "products/bulk_update_stocks"

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
            if response.status == 422:
                error = UnprocessableEntityError(**error_data)
                raise ShoplineAPIError(
                    status_code=422,
                    error=error
                )
            if response.status == 500:
                error = ServerError(**error_data)
                raise ShoplineAPIError(
                    status_code=500,
                    error=error
                )
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)