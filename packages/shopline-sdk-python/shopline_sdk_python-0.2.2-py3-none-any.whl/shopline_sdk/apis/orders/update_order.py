from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.order import Order
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.translatable import Translatable

class Params(BaseModel):
    """查询参数模型"""
    include_fields: Optional[List[Union[Literal['affiliate_campaign'], str]]] = Field(default=None, alias="include_fields[]")
    """Provide additional attributes in the response
      結果添加哪些參數"""
    fields: Optional[List[str]] = Field(default=None, alias="fields[]")
    """Only return the provided fields in the responses
      結果只包含輸入的參數
       This parameter will override include_fields[]
      此參數會覆蓋include_fields[]。"""


class CustomDataItemSchema(BaseModel):
    """Item model for custom_data"""
    value: Optional[str] = None
    field_id: Optional[str] = None


class DeliveryDataSchema(BaseModel):
    """Delivery Data
    運送資訊
    
    Able to update the fields below
    可修改以下欄位
    - location_code
    - location_name
    - store_address
    - recipient_name
    - recipient_phone"""
    location_code: Optional[str] = None
    location_name: Optional[str] = None
    store_address: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone: Optional[str] = None
    recipient_phone_country_code: Optional[str] = None

class Body(BaseModel):
    """请求体模型"""
    tracking_number: Optional[str] = None
    """Delivery Tracking Number
      物流追蹤號碼"""
    tracking_url: Optional[str] = None
    """Delivery Tracking url
      物流追蹤url"""
    delivery_provider_name: Optional[Translatable] = None
    ref_order_id: Optional[str] = None
    """For third party custom order id
      可供儲存第三方訂單ID"""
    custom_data: Optional[List[CustomDataItemSchema]] = None
    """Custom data
      自定義資料"""
    delivery_data: Optional[DeliveryDataSchema] = None
    """Delivery Data
      運送資訊
      
      Able to update the fields below
      可修改以下欄位
      - location_code
      - location_name
      - store_address
      - recipient_name
      - recipient_phone"""
    delivery_address: Optional[Dict[str, Any]] = None
    """Delivery Address Information
      運送地址資訊
      
      Able to update the fields below
      可修改以下欄位
      - country
      - country_code
      - address_1
      - address_2
      - city
      - state
      - postcode"""
    force_update: Optional[Union[Literal['delivery_data'], str]] = None
    """To skip filtering delivery_data fields if force_update = ['delivery_data'] is passed
       略過delivery_data的篩選。"""
    has_notes: Optional[bool] = None
    """Order has notes or not
       訂單是否有備註"""

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None, body: Optional[Body] = None
) -> Order:
    """
    Update Order
    
    To update an order with open API
    透過open API更新一筆訂單
    
    Path: PATCH /orders/{id}
    """
    # 构建请求 URL
    url = f"orders/{id}"

    # 构建查询参数
    query_params = {}
    if params:
        params_dict = params.model_dump(exclude_none=True, by_alias=True)
        for key, value in params_dict.items():
            if value is not None:
                query_params[key] = value

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.patch(
        url, params=query_params, json=json_data, headers=headers
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
        return Order(**response_data)