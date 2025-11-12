from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.sale_customer import SaleCustomer
from shopline_sdk.models.server_error import ServerError

class Params(BaseModel):
    """查询参数模型"""
    post_sales_user_ids: List[str]
    """The ID of the customer in the live room
      直播間中顧客的 ID"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[SaleCustomer]] = None

async def call(
    session: aiohttp.ClientSession, saleId: str, params: Optional[Params] = None
) -> Response:
    """
    Get sale customers
    
    To get sale customers
    取得直播間顧客的信息
    
    Path: GET /sales/{saleId}/customers
    """
    # 构建请求 URL
    url = f"sales/{saleId}/customers"

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