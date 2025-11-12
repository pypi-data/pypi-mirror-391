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
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    page: Optional[int] = None
    """Page
      頁數（第n頁）
      (Default: 1)"""
    per_page: Optional[int] = None
    """Numbers of Orders per page
      每頁顯示 n 筆資料
       (Default: 24, Max: 999)
      -
       *If there're many orders, it's suggested to set per_page number to 50
       如果訂單眾多，建議per_page至多設定50"""
    order_number: Optional[str] = None
    """訂單號碼 (order_number, merchant_order_number)"""
    customer_id: Optional[str] = None
    """顧客 ID"""
    customer_email: Optional[str] = None
    """顧客電郵"""
    name: Optional[str] = None
    """顧客、收件人名稱 (customer_name, delivery_address.recipient_name, delivery_data.recipient_name)"""
    phone_number: Optional[str] = None
    """電話號碼 (customer_phone, delivery_data.recipient_phone)"""
    delivery_data_tracking_number: Optional[str] = None
    """配送資料追蹤編號"""
    promotion_id: Optional[str] = None
    """促銷活動 ID"""
    item_id: Optional[str] = None
    """訂單項目 ID"""
    previous_id: Optional[str] = None
    """To fetch data for the next page, include the ID of the last order from the previous page. 
       用於拿取下一分頁資料，請帶入前一分頁的最後一筆訂單 ID 
      
       When fetching orders for the first page, this parameter is not required. 
       拿取第一頁訂單時，可以不用帶此參數"""
    query: Optional[str] = None
    """Support query order fields
      支援搜尋以下欄位
       product_name
       order_number
       customer_id
       customer_name
       customer_phone
       customer_email
       delivery_address.recipient_name
       delivery_data.recipient_name
       delivery_data.recipient_phone
       delivery_data.tracking_number
       promotion_id
       item_id*"""
    search_fields: Optional[str] = None
    """Targeted search fields
      搜尋欄位
       Default to 'default'
       Values allow
      
      
      <b>default</b>
       Support query order fields
      支援搜尋以下欄位
       product_name
       order_number
       customer_id
       customer_name
       customer_phone
       customer_email
       delivery_address.recipient_name
       delivery_data.recipient_name
       delivery_data.recipient_phone
       delivery_data.tracking_number
       promotion_id
       item_id*
      
      
      <b>phone_number</b>
       Support query order fields
      支援搜尋以下欄位
       customer_phone
       delivery_data.recipient_phone
      
      
      <b>order_number</b>
       Support query order fields
      支援搜尋以下欄位
       order_number
       merchant_order_number
      
      
      <b>customize_customer_info</b>
       Support query order fields
      支援搜尋以下欄位
       customer_info.value
      
      
      <b>social_user_name</b>
       Support query order fields
      支援搜尋以下欄位
       social_user_name"""
    shipped_before: Optional[str] = None
    """Filter orders by those shipped before specific time.
       取得 shipped_at 小於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    shipped_after: Optional[str] = None
    """Filter orders by those shipped after specific time.
       取得 shipped_at 大於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    arrived_before: Optional[str] = None
    """Filter orders by those arrived before specific time.
       取得 arrived_at 小於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    arrived_after: Optional[str] = None
    """Filter orders by those arrived after specific time.
       取得 arrived_at 大於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    collected_before: Optional[str] = None
    """Filter orders by those collected before specific time.
       取得 collected_at 小於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    collected_after: Optional[str] = None
    """Filter orders by those collected after specific time.
       取得 collected_at 大於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    returned_before: Optional[str] = None
    """Filter orders by those returned before specific time.
       取得 returned_at 小於指定時間的訂單(包含指定時間)
      -
      should use UTC time
      
       Note: Will only show returned status updated after 2019-06-01
       在2019/06/01之後產生的退貨狀態才能被搜尋出來"""
    returned_after: Optional[str] = None
    """Filter orders by those returned after specific time.
       取得 returned_at 大於指定時間的訂單(包含指定時間)
      -
      should use UTC time
      
       Note: Will only show returned status updated after 2019-06-01
      在2019/06/01之後產生的退貨狀態才能被搜尋出來"""
    cancelled_before: Optional[str] = None
    """Filter orders by those cancelled before specific time.
       取得 cancelled_at 小於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    cancelled_after: Optional[str] = None
    """Filter orders by those cancelled after specific time.
       取得 cancelled_at 大於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    paid_before: Optional[str] = None
    """Filter orders by those paid before specific time.
       取得 paid_at 小於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    paid_after: Optional[str] = None
    """Filter orders by those paid after specific time.
       取得 paid_at 大於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    updated_before: Optional[str] = None
    """Filter orders by those updated before specific time.
       取得 updated_at 小於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    updated_after: Optional[str] = None
    """Filter orders by those updated after specific time.
       取得 updated_at 大於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    status: Optional[Union[Literal['pending', 'removed', 'confirmed', 'completed', 'cancelled'], str]] = None
    """Status
      訂單狀態
      -
      Status allow
       pending 處理中
      removed 已刪除
       confirmed 已確認
      completed 已完成
       cancelled 已取消"""
    statuses: Optional[List[Union[Literal['pending', 'removed', 'confirmed', 'completed', 'cancelled'], str]]] = Field(default=None, alias="statuses[]")
    """Statuses
      多個訂單狀態
      -
      Status allow
       pending 處理中
      removed 已刪除
       confirmed 已確認
      completed 已完成
       cancelled 已取消"""
    payment_id: Optional[str] = None
    """Payment Method ID
      付款方式ID"""
    payment_status: Optional[Union[Literal['pending', 'failed', 'expired', 'completed', 'refunding', 'refunded', 'partially_refunded'], str]] = None
    """Payment Status
      付款狀態
      -
      Payment status allows
      pending 未付款(包含 temp 暫存狀態)
       failed 付款失敗
      expired 超過付款時間
       completed 已付款
      refunding 退款中
       refunded 已退款
      partially refunded 已部分退款"""
    delivery_option_id: Optional[str] = None
    """Delivery Option ID
      物流方式ID"""
    delivery_status: Optional[Union[Literal['pending', 'shipping', 'shipped', 'arrived', 'collected', 'returned', 'returning'], str]] = None
    """Delivery Status
      物流狀態 
      -
       Delivery status allows
       pending 備貨中
       shipping 發貨中
       shipped 已發貨
       arrived 已到達
       collected 已取貨
       returned 已退貨
       * returning 退貨中"""
    delivery_statuses: Optional[List[Union[Literal['pending', 'shipping', 'shipped', 'arrived', 'collected', 'returned', 'returning'], str]]] = Field(default=None, alias="delivery_statuses[]")
    """Delivery Statuses
      多個物流狀態 
      -
       Delivery status allows
       pending 備貨中
       shipping 發貨中
       shipped 已發貨
       arrived 已到達
       collected 已取貨
       returned 已退貨
       returning 退貨中"""
    affiliate_data_affiliate_source: Optional[str] = Field(default=None, alias="affiliate_data[affiliate_source]")
    """Keys allow to search:
      * affiliate_source(String)訂單來源
      (第三方夥伴適用)"""
    created_before: Optional[str] = None
    """Filter orders by those updated before specific time.
       取得 created_at 小於指定時間的訂單(包含指定時間)
      -
       *should use UTC time"""
    created_after: Optional[str] = None
    """Filter orders by those created after specific time.
       取得 created_at 大於指定時間的訂單(包含指定時間)
      -
      *should use UTC time"""
    created_by: Optional[str] = None
    """Filter orders by those created by specific channel.
       取得特定由渠道建立的訂單"""
    order_by: Optional[Union[Literal['asc', 'desc'], str]] = None
    """Order responses items by created time in ascending/descending order.
       訂單按訂單創造日期順序或倒序排序。
       If sort_by is passed, Order the record by the sort_by value in asc/desc order.
       如果傳入sort_by，則按照sort_by的參數順序或倒序排序。"""
    sort_by: Optional[Union[Literal['created_at', 'total'], str]] = None
    """Sort responses items by created_at or total.
       訂單按訂單創造日期或商品總價排序。 If order_by is not passed, by default showing records in descending order.
       如果沒有傳入order_by, 則按倒序排序。"""
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
    Search Orders
    
    To search orders with specific conditions.
    利用特殊條件搜尋訂單列表。
    
    Path: GET /orders/search
    """
    # 构建请求 URL
    url = "orders/search"

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
        return Response(**response_data)