from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.delivery_option import DeliveryOption
from shopline_sdk.models.translatable import Translatable


class StorePickupOptionSchema(BaseModel):
    """Model for store_pickup_option"""
    config_fields: Optional[Dict[str, Dict[str, Any]]] = None


class AddressesItemSchema(BaseModel):
    """Item model for addresses"""
    level_1_translations: Optional[Translatable] = None
    level_2_translations: Optional[Translatable] = None
    level_3_translations: Optional[Translatable] = None
    store_name_translations: Optional[Translatable] = None
    store_address_translations: Optional[Translatable] = None
    instruction_translations: Optional[Translatable] = None

class Body(BaseModel):
    """请求体模型"""
    store_pickup_option: Optional[StorePickupOptionSchema] = None
    addresses: Optional[List[AddressesItemSchema]] = None

class Response(BaseModel):
    """响应体模型"""
    delivery_option: Optional[DeliveryOption] = None
    errors: Optional[List[str]] = None

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> Response:
    """
    Update Delivery Option(Store Pickup)'s Store Information
    
    To update a delivery option(store pickup)'s store information.
    更新一個為什門市自取的送貨方式的門市資訊。
    
    Path: PUT /delivery_options/{id}/stores_info
    """
    # 构建请求 URL
    url = f"delivery_options/{id}/stores_info"

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
        return Response(**response_data)