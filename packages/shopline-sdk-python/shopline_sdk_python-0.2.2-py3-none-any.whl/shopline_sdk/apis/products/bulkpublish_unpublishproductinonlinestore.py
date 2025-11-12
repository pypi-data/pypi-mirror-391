from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.status import status


class ProductsItemSchema(BaseModel):
    """Item model for products"""
    id: Optional[str] = None
    """The id of the product that will be published/unpublished.
       Max delete 100 products at a time.
       需要上架/下架的商品id，每次最多只能上架/下架100個商品。"""
    status: Optional[status] = None

class Body(BaseModel):
    """请求体模型"""
    products: Optional[List[ProductsItemSchema]] = None

class Response(BaseModel):
    """响应体模型"""
    updated_product_ids: Optional[List[str]] = None
    errors: Optional[List[Dict[str, Any]]] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> Response:
    """
    Bulk Publish/Unpublish Product in Online Store
    
    To bulk publish/unpublish products in Online Store.
     在網店批量上架/下架商品。
    
    Path: PUT /products/status/bulk
    """
    # 构建请求 URL
    url = "products/status/bulk"

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
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)