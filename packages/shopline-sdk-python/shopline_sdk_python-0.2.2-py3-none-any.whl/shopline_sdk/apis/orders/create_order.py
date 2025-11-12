from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.order import Order
from shopline_sdk.models.order_delivery_address import OrderDeliveryAddress
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

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


class OrderSchema(BaseModel):
    """Model for order"""
    delivery_option_id: str
    """ID of Delivery Option
      出貨方式之ID
      -
      *Currently not allowed third party delivery providers
      暫不支援第三方物流串接方式"""
    payment_method_id: str
    """ID of Payment Option
      付款方式之ID
      -
      *Currently not allowed third party payment service
      暫不支援第三方金流串接方式"""
    subtotal: float
    """Price Total for all order items
      訂單小計，包含所有商品總價"""
    total: float
    """Final price total, including credits and discounts deducted.
      付款總金額,為訂單小計扣除購物金與折扣
      -
      *Delivery fee and payment fee are not calculated
      目前尚未支援附加費與運費的計入"""
    items: List[Dict[str, Any]]
    """Order product Item Data
      訂單中商品資訊"""
    customer_id: Optional[str] = None
    """Customer ID
      顧客ID
       * Required to be passed between customer_id and customer_email.
       * 必須傳入customer_id和customer_email其中一個"""
    customer_email: Optional[str] = None
    """Customer's Email
      顧客Email
       * Required to be passed between customer_id and customer_email.
       * 必須傳入customer_id和customer_email其中一個"""
    customer_phone: Optional[str] = None
    """Customer's Phone
      顧客電話"""
    customer_phone_country_code: Optional[str] = None
    customer_name: Optional[str] = None
    """Customer's Name
      顧客名字"""
    customer_birthday: Optional[str] = None
    """Customer's Birthday
      顧客生日"""
    customer_gender: Optional[Union[Literal['male', 'female', 'other'], str]] = None
    """Customer's Gender
      顧客性別"""
    coupon_item_ids: Optional[List[str]] = None
    """Coupon Item ids
       優惠劵商品id"""
    expired_at: Optional[str] = None
    """Order's Expiration Date/Time
       Order到期時日"""
    confirmed_at: Optional[str] = None
    """Order's Confirmation Date/Time
       訂單確認時日"""
    ga_tracked: Optional[bool] = None
    auth_token_expired_at: Optional[str] = None
    """Auth Token's Expiration Date/Time
       Auth Token到期時日"""
    order_remarks: Optional[str] = None
    """Order's Remark
      訂單備注"""
    created_from: Optional[str] = None
    delivery_address: OrderDeliveryAddress
    user_credit: Optional[int] = None
    """Credits used for the order
      訂單所使用之折抵購物金"""
    member_point: Optional[float] = None
    """Applied Member Point
      已使用會員點數"""
    opt_in_auto_reward: Optional[bool] = None
    """Apply "Order Reward Credits" and "Reward Campaign" automatically
       自動套用「滿額送購物金」及「回饋活動（含回饋購物金及回饋點數）」
       -
      *Default: false"""

class Body(BaseModel):
    """请求体模型"""
    order: Optional[OrderSchema] = None
    is_registering_as_member: Optional[bool] = None
    """Do you want to set the customer as a member?
      是否要將此筆訂單顧客設為會員？
      -
      *Default: false"""
    is_inventory_fulfillment: Optional[bool] = None
    """Do you want to deduct the inventory numbers after the order is created?
      此筆訂單是否要扣掉庫存？
      -
      *Default:false"""
    mail_notify: Optional[bool] = None
    """Do you want to notify the customer of the order creation by email ?
      此筆訂單成立之後是否要通知顧客？
      -
      *Default:false"""

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None, body: Optional[Body] = None
) -> Order:
    """
    Create Order
    
    To create an order with open API
    透過open API創建一筆新訂單
    
    Path: POST /orders
    """
    # 构建请求 URL
    url = "orders"

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
    async with session.post(
        url, params=query_params, json=json_data, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
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
        return Order(**response_data)