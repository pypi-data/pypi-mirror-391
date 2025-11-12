from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.addon_product import AddonProduct
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.translatable import Translatable

class Params(BaseModel):
    """查询参数模型"""
    limit: Optional[int] = None
    """Number of Order by request"""
    next_product_id: Optional[str] = None
    """The last Product Id of the products in the previous request."""
    next_quantity: Optional[int] = None
    """The last Quantity of the products in the previous request."""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Dict[str, Any]]] = None
    cursor: Optional[Dict[str, Any]] = None

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None
) -> Response:
    """
    Get Products Sales Ranking of Campaign
    
    To get products sales ranking of campaign.
    
    Path: GET /affiliate_campaigns/{id}/get_products_sales_ranking
    """
    # 构建请求 URL
    url = f"affiliate_campaigns/{id}/get_products_sales_ranking"

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