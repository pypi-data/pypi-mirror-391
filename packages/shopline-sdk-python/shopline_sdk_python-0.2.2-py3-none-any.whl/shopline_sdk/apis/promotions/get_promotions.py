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
    customer_id: Optional[str] = None
    """用戶id"""
    scope: Optional[Union[Literal['valid', 'invalid'], str]] = None
    """promotion是否失效 (搭配customer_id使用)"""
    promotion_ids: Optional[List[str]] = None
    """Filter promotions by IDs.
       The promotion_ids parameter must be used standalone.
       透過 IDs 獲取相關優惠活動，此參數須單獨使用。"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    per_page: Optional[int] = None
    """Numbers of Orders per Page
      每頁顯示 n 筆資料
       上限 100"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Promotion]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get Promotions
    
    To get detailed information of couple promotions sorted by time
    利用時間範圍選取與排序獲取數筆優惠活動
    
    Path: GET /promotions
    """
    # 构建请求 URL
    url = "promotions"

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