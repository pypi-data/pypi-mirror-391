from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.product_stock import ProductStock
from shopline_sdk.models.server_error import ServerError

class Body(BaseModel):
    """请求体模型"""
    warehouse_id: str
    """Warehouse’s id
      倉庫 id
      -----
      Only warehouse with status "active" can be updated
      只有 status “active” 的 warehouse stock 的可以更新"""
    quantity: float
    """Quantity
      (新增/減少)商品數量
      
      Negative number is allowed
      允許更新庫存為負值"""
    is_replace: Optional[bool] = None
    """Whether replacing the original quantity
      是否取代原本數量
      
      true: replace the product's quantity with the number you provided
      取代原本數量
      
      false: increase/decrease the quantity with the number you provided
      增加/減少數量"""

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> ProductStock:
    """
    Update Addon Product Stock
    
    To update the addon product stock with its ID
     使用商品 ID 更新加購品在各個倉庫的庫存
    
    Path: PUT /addon_products/{id}/stocks
    """
    # 构建请求 URL
    url = f"addon_products/{id}/stocks"

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
        return ProductStock(**response_data)