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
    session: aiohttp.ClientSession
) -> Response:
    """
    Bulk Delete Product Review Comments
    
    To bulk delete product review comments.
    批量刪除商品評價。
     ids of product review comments
    商品評價id
     example:in:5d7a026ce388095474c7b5fa,5e44c892e3880946bb3ababd
    
    Path: DELETE /product_review_comments/bulk
    """
    # 构建请求 URL
    url = "product_review_comments/bulk"

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