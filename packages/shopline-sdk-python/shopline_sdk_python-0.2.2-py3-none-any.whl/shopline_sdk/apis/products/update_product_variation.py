from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.product import Product
from shopline_sdk.models.update_product_variation_body import UpdateProductVariationBody as Body

async def call(
    session: aiohttp.ClientSession, product_id: str, id: str, body: Optional[Body] = None
) -> Product:
    """
    Update Product Variation
    
    Update information of an existing product variation.
    針對現有規格商品做訊息更新
    
    Path: PUT /products/{product_id}/variations/{id}
    """
    # 构建请求 URL
    url = f"products/{product_id}/variations/{id}"

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
        return Product(**response_data)