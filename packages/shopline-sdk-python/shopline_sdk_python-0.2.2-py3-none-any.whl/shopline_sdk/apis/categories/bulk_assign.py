from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.category import Category
from shopline_sdk.models.merchant import Merchant
from shopline_sdk.models.product import Product
from shopline_sdk.models.server_error import ServerError

class Body(BaseModel):
    """请求体模型"""
    product_ids: List[str]
    """Array of product id
      商品id"""
    category_ids: List[str]
    """Array of category id
      商品分類id"""
    is_bulk_remove: Optional[bool] = None
    """bulk remove or add, default false
      批量添加還是移除,默認為false"""
    unset_other_categories: Optional[bool] = None
    """if products in other categories, unset other categories, default false
       如果商品在其他分類，是否從其他分類刪除，默認為false"""

class Response(BaseModel):
    """响应体模型"""
    result: Optional[List[Dict[str, Any]]] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> Response:
    """
    Bulk Assign
    
    To add or remove bulk products to categories
    從指定分類批量添加或移除商品
    
    Path: POST /categories/bulk_assign
    """
    # 构建请求 URL
    url = "categories/bulk_assign"

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