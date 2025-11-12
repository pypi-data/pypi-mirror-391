from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.store_credit import StoreCredit

class Params(BaseModel):
    """查询参数模型"""
    created_at_after: Optional[str] = None
    """Filter store credits by those created after specific time.
       取得 created_at 大於指定時間的購物金(包含指定時間)
       *Should use UTC time'"""
    created_at_before: Optional[str] = None
    """Filter store credits by those create before specific time.
       取得 created_at 小於指定時間的購物金(包含指定時間)
       *Should use UTC time'"""
    end_at_after: Optional[str] = None
    """Filter store credits by those end after specific time.
       取得 end_at 大於指定時間的購物金(包含指定時間)
       *Should use UTC time'"""
    end_at_before: Optional[str] = None
    """Filter store credits by those end before specific time.
       取得 end_at 小於指定時間的購物金(包含指定時間)
       *Should use UTC time'"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    per_page: Optional[int] = None
    """Numbers of Orders per Page
      每頁顯示 n 筆資料"""
    excludes: Optional[List[str]] = Field(default=None, alias="excludes[]")
    """Could exclude certain parameters in the response
      結果要排除哪些參數"""
    fields: Optional[List[str]] = Field(default=None, alias="fields[]")
    """Could only show certain parameters in the response
      結果只顯示哪些參數"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[StoreCredit]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get Store Credits
    
    To get customers store credits
    獲取商店購物金紀錄
    
    Path: GET /user_credits
    """
    # 构建请求 URL
    url = "user_credits"

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