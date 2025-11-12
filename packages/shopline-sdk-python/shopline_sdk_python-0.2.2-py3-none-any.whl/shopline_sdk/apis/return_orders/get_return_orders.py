from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.return_orders import ReturnOrders

class Params(BaseModel):
    """查询参数模型"""
    order_id: Optional[str] = None
    """Order ID, the other parameters will be ineffective if passed.
       訂單ID, 如果傳了其他參數將會失效"""
    updated_after: Optional[str] = None
    """Filter data by those updated after specific time.
       取得 updated_at 大於指定時間的退貨單(包含指定時間)
       *Should use UTC time'"""
    updated_before: Optional[str] = None
    """Filter data by those updated before specific time.
       取得 updated_at 小於指定時間的退貨單(包含指定時間)
       *Should use UTC time'"""
    created_after: Optional[str] = None
    """Filter data by those created after specific time.
       取得 created_at 大於指定時間的退貨單(包含指定時間)
       *Should use UTC time'"""
    created_before: Optional[str] = None
    """Filter data by those created before specific time.
       取得 created_at 小於指定時間的退貨單(包含指定時間)
       *Should use UTC time'"""
    status_filter: Optional[Union[Literal['pending', 'confirmed', 'completed', 'cancelled'], str]] = None
    """Order Status
      退货訂單狀態"""
    payment_status_filter: Optional[Union[Literal['pending', 'refunded'], str]] = None
    """Order payment status
      訂單退款狀態"""
    delivery_status_filter: Optional[Union[Literal['return_collected', 'returning'], str]] = None
    """Order delivery status
      訂單退貨狀態"""
    inspect_status_filter: Optional[Union[Literal['pending', 'inspected'], str]] = None
    """Order inspect status
      驗貨狀態"""
    query: Optional[str] = None
    """Query
      用於搜索退貨單，可搜索的字段有: "customer_phone", "customer_name", "customer_email", "delivery_data.recipient_name", "delivery_address.recipient_name", "tracking_number", "delivery_data.recipient_phone", "return_order_number" """
    per_page: Optional[int] = None
    """Numbers of Return Orders per Page
      每頁顯示 n 筆資料"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    previous_id: Optional[str] = None
    """前一筆退貨單 ID"""

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> ReturnOrders:
    """
    Get return orders
    
    To retrieve return order list
    獲取退貨單列表
    
    Path: GET /return_orders
    """
    # 构建请求 URL
    url = "return_orders"

    # 构建查询参数
    query_params = {}
    if params:
        params_dict = params.model_dump(exclude_none=True, by_alias=True)
        for key, value in params_dict.items():
            if value is not None:
                query_params[key] = value

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, params=query_params, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return ReturnOrders(**response_data)