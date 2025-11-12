from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.product_subscription import ProductSubscription

class Params(BaseModel):
    """查询参数模型"""
    per_page: Optional[int] = None
    """Numbers of Products per page
      每頁顯示 n 筆資料"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    previous_id: Optional[str] = None
    """Previous ID
      上一頁的ID"""
    id: Optional[str] = None
    """Only show specific products based on IDs
      結果只顯示哪些商品"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[ProductSubscription]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get a list of product subscriptions
    
    Retrieve information of multiple product subscriptions
    抓取多筆定期購的信息
    
    Path: GET /product_subscriptions
    """
    # 构建请求 URL
    url = "product_subscriptions"

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