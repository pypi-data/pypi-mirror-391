from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError


class DataItemSchema(BaseModel):
    """Item model for data"""
    product_id: Optional[str] = None
    """The Product ID
      欲排序的商品 ID"""
    ancestor: Optional[str] = None
    """Previous Product ID
      欲排序的前一個商品 ID"""
    descendant: Optional[str] = None
    """Previous Product ID
      欲排序的後一個商品 ID"""

class Body(BaseModel):
    """请求体模型"""
    data: Optional[List[DataItemSchema]] = None
    """Product ID, Ancestor, Descendant
      批量更新的商品 ID"""

class Response(BaseModel):
    """响应体模型"""
    job_tracker_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> Response:
    """
    Bulk Update Category Product Sorting
    
    To bulk update category product sorting.
    批量更新分類中商品的排序
    
    Path: PUT /categories/{id}/products_sorting
    """
    # 构建请求 URL
    url = f"categories/{id}/products_sorting"

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