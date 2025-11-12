from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.payment import Payment

class Params(BaseModel):
    """查询参数模型"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    per_page: Optional[int] = None
    """Numbers of Orders per Page
      每頁顯示 n 筆資料"""
    sort_by: Optional[Union[Literal['asc', 'desc'], str]] = None
    """Setting sorting direction
      設定時間排序"""
    order_by: Optional[Union[Literal['created_at', 'priority'], str]] = None
    """Setting sorting attribute
      設定排序使用值"""
    updated_after: Optional[str] = None
    """Filter payments by those updated after specific time.
      取得 updated_at 大於指定時間的付款方式(包含指定時間)
       *Should use UTC time'"""
    updated_before: Optional[str] = None
    """Filter payments by those updated before specific time.
      取得 updated_at 小於指定時間的付款方式(包含指定時間)
       *Should use UTC time'"""
    excludes: Optional[List[str]] = Field(default=None, alias="excludes[]")
    """Could exclude certain parameters in the response
      結果要排除哪些參數"""
    fields: Optional[List[str]] = Field(default=None, alias="fields[]")
    """Could only show certain parameters in the response
      結果只顯示哪些參數"""
    channel_id: Optional[str] = None
    """Filter payments by channel approved sl-payments methods.
      取得門店可用付款方式"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Payment]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get Payments
    
    To get all kinds of payment methods with open API
    透過open API獲取所有的付款方式
    
    Path: GET /payments
    """
    # 构建请求 URL
    url = "payments"

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