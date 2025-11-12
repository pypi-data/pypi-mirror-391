from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.product_review_comment import ProductReviewComment
from shopline_sdk.models.update_product_review_comment_body import UpdateProductReviewCommentBody as Body

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> ProductReviewComment:
    """
    Update Product Review Comment
    
    To update a product review comment by id.
    以id更新某一商品評價。
    
    Path: PUT /product_review_comments/{id}
    """
    # 构建请求 URL
    url = f"product_review_comments/{id}"

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
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return ProductReviewComment(**response_data)