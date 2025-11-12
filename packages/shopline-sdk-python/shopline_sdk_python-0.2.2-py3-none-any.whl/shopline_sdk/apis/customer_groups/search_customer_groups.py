from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.customer_group import CustomerGroup
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.server_error import ServerError
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
      customer_group_name"""
    sort_by: Optional[str] = None
    """Setting sort by created time
      設定依照建立時間排序
      (Default: desc)"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[CustomerGroup]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Search Customer Groups
    
    To search customer groups with specific conditions.
    利用特殊條件搜尋顧客分群。
    
    Path: GET /customer_groups/search
    """
    # 构建请求 URL
    url = "customer_groups/search"

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