from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.product_review_setting import ProductReviewSetting
from shopline_sdk.models.server_error import ServerError

async def call(
    session: aiohttp.ClientSession
) -> ProductReviewSetting:
    """
    Get Product Review Setting
    
    To retrieve the setting of product review
    獲取商品評價設定
    
    Path: GET /settings/product_review
    """
    # 构建请求 URL
    url = "settings/product_review"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, headers=headers
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
        return ProductReviewSetting(**response_data)