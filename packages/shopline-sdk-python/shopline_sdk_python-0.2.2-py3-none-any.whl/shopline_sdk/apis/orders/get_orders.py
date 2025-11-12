from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.order import Order
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.server_error import ServerError

class Params(BaseModel):
    """查询参数模型"""
    default_visible_channels: Optional[bool] = None
    """filter online orders when the prop is true.
       篩選線上訂單"""
    updated_after: Optional[str] = None
    """Filter orders by those updated after specific time.
       取得 updated_at 大於指定時間的分類(包含指定時間)
       *Should use UTC time"""
    updated_before: Optional[str] = None
    """Filter orders by those updated before specific time.
       取得 updated_at 小於指定時間的分類(包含指定時間)
       *Should use UTC time"""
    created_after: Optional[str] = None
    """Filter orders by those updated after specific time.
       取得 created_at 大於指定時間的分類(包含指定時間)
       *Should use UTC time"""
    created_before: Optional[str] = None
    """Filter orders by those updated before specific time.
       取得 created_at 小於指定時間的分類(包含指定時間)
       *Should use UTC time"""
    order_ids: Optional[List[str]] = None
    """Order IDs
      指定Order ID"""
    previous_id: Optional[str] = None
    """To fetch data for the next page, include the ID of the last order from the previous page. 
       用於拿取下一分頁資料，請帶入前一分頁的最後一筆訂單 ID 
      
       When fetching orders for the first page, this parameter is not required. 
       拿取第一頁訂單時，可以不用帶此參數"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    per_page: Optional[int] = None
    """Numbers of Orders per Page
      每頁顯示 n 筆資料"""
    sort_by: Optional[Union[Literal['asc', 'desc'], str]] = None
    """Setting sort by created time
      設定創建時間排序"""
    customer_id: Optional[str] = None
    """filter by customer ID
      篩選顧客 ID"""
    include_fields: Optional[List[Union[Literal['affiliate_campaign'], str]]] = Field(default=None, alias="include_fields[]")
    """Provide additional attributes in the response
      結果添加哪些參數"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Order]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get Orders
    
    To get detailed information of couple orders sorted by time
    利用時間範圍選取與排序獲取數筆訂單資料
    
    Path: GET /orders
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

    # 发起 HTTP 请求
    async with session.get(
        url, params=query_params, headers=headers
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
        return Response(**response_data)