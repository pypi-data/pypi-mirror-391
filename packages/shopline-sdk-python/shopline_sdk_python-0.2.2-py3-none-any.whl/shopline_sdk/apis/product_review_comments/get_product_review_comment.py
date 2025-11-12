from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.product_review_comment import ProductReviewComment

async def call(
    session: aiohttp.ClientSession, id: str
) -> ProductReviewComment:
    """
    Get Product Review Comment
    
    To retrieve one of the product review comments by id.
    以id抓取某一商品評價。
    
    Path: GET /product_review_comments/{id}
    """
    # 构建请求 URL
    url = f"product_review_comments/{id}"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
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
        return ProductReviewComment(**response_data)