from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.customer import Customer
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unauthorized_error import UnauthorizedError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    page: Optional[int] = None
    """Page
      頁數
      (Default: 1)"""
    per_page: Optional[int] = None
    """Numbers of Customers per page
      每頁顯示 n 筆資料
      (Default: 24, Max: 999)"""
    query: Optional[str] = None
    """Support searching fields below:
      支援搜尋以下欄位:
      name
      email
      phones
      mobile_phone"""
    search_fields: Optional[List[str]] = None
    """To specify searching fields 
      指定搜尋欄位:
      name
      email
      phones
      mobile_phone"""
    id: Optional[List[str]] = Field(default=None, alias="id[]")
    """Customer's ID list
      顧客編號列表"""
    name: Optional[str] = None
    """Customer's Name
      顧客姓名
      -
      *Support equal or not equal.
      支援 等於 或 不等於"""
    email: Optional[str] = None
    """Customer's Email
      顧客Email
      -
      *Support equal or not equal.
      支援 等於 或 不等於"""
    phone: Optional[str] = None
    """Customer's Phone
      顧客電話
      -
      Support equal or not equal.
      支援 等於 或 不等於"""
    phones: Optional[str] = None
    """Customer's Phones
      顧客電話
      -
      Support equal or not equal.
      支援 等於 或 不等於"""
    mobile_phone: Optional[str] = None
    """Customer's Mobile Phone
      顧客手機
      -
      Support equal or not equal.
      支援 等於 或 不等於."""
    gender: Optional[Union[Literal['male', 'female', 'other'], str]] = None
    """Customer's Gender
      顧客性別
      -
      Gender allows
      male 男性
      female 女性
      other 其他
      
      Support equal or not equal.
      支援 等於 或 不等於."""
    membership_tier_id: Optional[str] = None
    """Membership Tier
      顧客等級
      -
      With blank will return customers without  membership tier
      當帶入空值，將回傳無會員等級之顧客
      
      With not: will return customers with membership tier
      當帶入not:，將回傳有會員等級之顧客
      
      *Support equal or not equal.
      支援 等於 或 不等於."""
    created_at: Optional[str] = None
    """Filter customers by created time
      以顧客創造時間作為搜尋依據
      -
      Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於
      
      Please fill in to the second level. Default value is 00:00:00 if only fill in dates.
      請輸入至秒數，若只輸入日期，則會自動帶入當天00:00:00"""
    updated_at: Optional[str] = None
    """Filter customers by created time
      以顧客更新時間作為搜尋依據
      -
      *Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    registered_at: Optional[str] = None
    """Filter customers by registered time
      以顧客註冊時間作為搜尋依據
      -
      *Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    birthday: Optional[str] = None
    """Filter customers by birthday
      以顧客生日作為搜尋依據
      -
      *Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    birth_month: Optional[str] = None
    """Filter customers by birth month
      以顧客生日月份作為搜尋依據
      -
       *Support equal or not equal or less than or less than or equal or not equal or greater than or greater than or equal
       支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    credit_balance: Optional[str] = None
    """Filter customers by credit balance
      以購物金作為搜尋依據
      -
      *Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    is_member: Optional[bool] = None
    """Filter member customers.
      搜尋是會員的顧客"""
    is_blacklisted: Optional[bool] = None
    """Filter Blacklisted Customers.
      搜尋是黑名單的顧客"""
    is_subscribed_marketing_email: Optional[bool] = None
    """Filter Customers by Marketing Acceptance.
      搜尋接受優惠宣傳的顧客"""
    ref_user_id: Optional[str] = None
    """Third party custom customer id
      第三方儲存之顧客ID"""
    tags: Optional[str] = None
    """Custom tags
      自定義標籤"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Customer]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Search Customers
    
    To search customers with specific conditions.
    利用特殊條件搜尋顧客列表。
    
    Path: GET /customers/search
    """
    # 构建请求 URL
    url = "customers/search"

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
            if response.status == 401:
                error = UnauthorizedError(**error_data)
                raise ShoplineAPIError(
                    status_code=401,
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
        return Response(**response_data)