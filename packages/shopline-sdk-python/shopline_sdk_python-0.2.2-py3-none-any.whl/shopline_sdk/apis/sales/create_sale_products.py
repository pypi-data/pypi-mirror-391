from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.sale_product import SaleProduct
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError


class ProductsItemSchema(BaseModel):
    """Item model for products"""
    product_id: str
    custom_numbers: Optional[List[str]] = None
    custom_keys: Optional[List[str]] = None
    variations: Optional[List[Dict[str, Any]]] = None

class Body(BaseModel):
    """请求体模型"""
    products: List[ProductsItemSchema]

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[SaleProduct]] = None

async def call(
    session: aiohttp.ClientSession, saleId: str, body: Optional[Body] = None
) -> Response:
    """
    Create sale products
    
    To create sale products
    新增直播商品
    
    Path: POST /sales/{saleId}/products
    """
    # 构建请求 URL
    url = f"sales/{saleId}/products"

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