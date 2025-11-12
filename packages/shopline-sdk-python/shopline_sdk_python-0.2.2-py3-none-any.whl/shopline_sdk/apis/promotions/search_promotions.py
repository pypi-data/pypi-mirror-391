from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.promotion import Promotion

class Params(BaseModel):
    """查询参数模型"""
    updated_after: Optional[str] = None
    """Filter data by those updated after specific time.
       取得 updated_at 大於指定時間的優惠活動(包含指定時間)
       *Should use UTC time'"""
    updated_before: Optional[str] = None
    """Filter data by those updated before specific time.
       取得 updated_at 小於指定時間的優惠活動(包含指定時間)
       *Should use UTC time'"""
    created_after: Optional[str] = None
    """Filter data by those created after specific time.
       取得 created_at 大於指定時間的優惠活動(包含指定時間)
       *Should use UTC time'"""
    created_before: Optional[str] = None
    """Filter data by those created before specific time.
       取得 created_at 小於指定時間的優惠活動(包含指定時間)
       *Should use UTC time'"""
    start_after: Optional[str] = None
    """Filter data by those updated after specific time.
       取得 start_at 大於指定時間的優惠活動(包含指定時間)
       *Should use UTC time'"""
    start_before: Optional[str] = None
    """Filter data by those updated before specific time.
       取得 start_at 小於指定時間的優惠活動(包含指定時間)
       *Should use UTC time'"""
    end_after: Optional[str] = None
    """Filter data by those updated after specific time.
       取得 end_at 大於指定時間的優惠活動(包含指定時間)
       *Should use UTC time'"""
    end_before: Optional[str] = None
    """Filter data by those updated before specific time.
       取得 end_at 小於指定時間的優惠活動(包含指定時間)
       *Should use UTC time'"""
    apply_method: Optional[Union[Literal['auto_apply', 'coupon', 'affiliate_campaign'], str]] = None
    """使用方式"""
    coupon_type: Optional[List[Union[Literal['draw', 'single', 'multi'], str]]] = Field(default=None, alias="coupon_type[]")
    """優惠券類別"""
    status: Optional[Union[Literal['active', 'draft', 'hidden'], str]] = None
    """狀態"""
    available_count: Optional[str] = None
    """剩餘可抽取量"""
    discount_on: Optional[Union[Literal['order', 'item', 'category'], str]] = None
    """優惠作用範圍"""
    discount_type: Optional[List[Union[Literal['percentage', 'amount', 'free_shipping', 'gift', 'addon', 'bundle_pricing', 'bundle_group', 'bundle_percentage', 'bundle_amount', 'bundle_gift', 'bundle_group_percentage', 'bundle_group_amount', 'bundle_group_gift', 'buyandget_free', 'buyandget_pricing', 'buyandget_percentage', 'subscription_gift', 'subscription_percentage', 'subscription_amount', 'member_point_redeem_gift', 'credit_reward', 'point_reward', 'earn_purchase_points'], str]]] = Field(default=None, alias="discount_type[]")
    """優惠類別"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    per_page: Optional[int] = None
    """Numbers of Orders per Page
      每頁顯示 n 筆資料"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Promotion]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Search Promotions
    
    Search Promotion
    
    Path: GET /promotions/search
    """
    # 构建请求 URL
    url = "promotions/search"

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
        return Response(**response_data)