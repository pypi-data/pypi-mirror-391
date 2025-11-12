from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.addon_product import AddonProduct
from shopline_sdk.models.server_error import ServerError

class Body(BaseModel):
    """请求体模型"""
    sku: Optional[str] = None
    """Addon Product sku
      加購品的商品貨號"""
    quantity: Optional[int] = None
    """This value should be between -9999999 and 9999999.
       數值必須在 -9999999 和 9999999 之間。"""
    replace: Optional[bool] = None
    """Whether replacing the original quantity
      是否取代原本數量
       - 
       true: replace the product's quantity with the number you provided
      取代原本數量
      
       false: increase/decrease the quantity with the number you provided
      增加/減少數量" """

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> AddonProduct:
    """
    Bulk Update Addon Product Quantity by SKU
    
    Update all add-on products quantity by input SKU
    更新所有相同商品貨號加購品的庫存數量
    
    Path: PUT /addon_products/update_quantity
    """
    # 构建请求 URL
    url = "addon_products/update_quantity"

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
        return AddonProduct(**response_data)