from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.translatable import Translatable


class DataItemSchema(BaseModel):
    """Item model for data"""
    product_ids: Optional[List[str]] = None
    """Maximum allows 1000 product_id per action
       上限 1000 個商品 ID"""
    label: Optional[Dict[str, Any]] = None
    """remove product's label if label is empty.
       label 為空代表移除促銷標籤"""

class Body(BaseModel):
    """请求体模型"""
    data: Optional[List[DataItemSchema]] = None
    """One item means one operation on a batch of products. Maximum allows 5 operations per request.
       一個 item 代表對一批商品做相同操作，一次請求上限 5 個操作"""

class Response(BaseModel):
    """响应体模型"""
    data: Optional[List[Any]] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> Response:
    """
    Batch Update (add/remove) current product labels
    
    Add or Remove current product labels.
    
    Path: PATCH /products/labels
    """
    # 构建请求 URL
    url = "products/labels"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.patch(
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