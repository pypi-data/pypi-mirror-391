from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.bad_request_error import BadRequestError
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.product import Product
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    price: Optional[float] = None
    """Price (Note: Cannot be set to null. Product with a price of 0 cannot be sold.)
       原價格 (備註：不能設定為null。價格為0的商品不能被售出)"""
    price_sale: Optional[float] = None
    """Price on sale  (Note: Cannot be set to null. 
       Product with a price_sale of 0 will be sold at its original price.)
      
      特價 (備註：不能設定為null。特價為0的商品會以原價售出）"""
    cost: Optional[float] = None
    """Cost (Note: Cannot be set to null)
       成本 (備註：不能設定為null)"""
    member_price: Optional[float] = None
    """Member Price
      會員價"""
    retail_price: Optional[float] = None
    """Retail Price
      零售價"""
    product_price_tiers: Optional[Dict[str, str]] = None
    """Membership tier's ID
      會員等級ID"""

async def call(
    session: aiohttp.ClientSession, productId: str, body: Body
) -> Product:
    """
    Update Product Price
    
    To update product's price with open API
    透過open API 更新商品價格
    
    Path: PUT /products/{productId}/update_price
    """
    # 构建请求 URL
    url = f"products/{productId}/update_price"

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
            if response.status == 404:
                error = NotFoundError(**error_data)
                raise ShoplineAPIError(
                    status_code=404,
                    error=error
                )
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
        return Product(**response_data)