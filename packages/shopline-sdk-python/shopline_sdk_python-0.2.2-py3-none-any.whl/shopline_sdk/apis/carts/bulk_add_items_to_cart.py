from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError


class ItemsItemSchema(BaseModel):
    """Item model for items"""
    product_id: Optional[str] = None
    """Product ID
       商品 ID"""
    type: Optional[str] = None
    """The Type of Item
       購物車物品類型"""
    created_by: Optional[str] = None
    """The Source of Item
       購物車物品加入的來源"""
    quantity: Optional[float] = None
    """Quantity
       數量"""
    variation_id: Optional[str] = None
    """Product Variation ID
       商品規格 ID"""
    item_price: Optional[Dict[str, Any]] = None
    """Custom Price（Use this field when type is custom discount）
       自訂折扣/商品價格（當類型是自訂折扣/商品，請在此欄位填寫價格）"""
    item_data: Optional[Dict[str, Any]] = None
    """Data of the cart item
      
        購物車物品類型資料"""

class Body(BaseModel):
    """请求体模型"""
    items: Optional[List[ItemsItemSchema]] = None

class Response(BaseModel):
    """响应体模型"""
    code: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, id: str, body: Body
) -> Response:
    """
    Bulk Add Items to Cart
    
    Bulk add items to cart.
     購物車加入商品
    
    Path: POST /carts/{id}/items
    """
    # 构建请求 URL
    url = f"carts/{id}/items"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.post(
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
        return Response(**response_data)