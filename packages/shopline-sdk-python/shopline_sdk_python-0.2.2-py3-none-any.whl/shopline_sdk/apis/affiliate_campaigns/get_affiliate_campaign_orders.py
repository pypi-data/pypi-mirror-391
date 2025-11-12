from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.affiliate_campaign_orders import AffiliateCampaignOrders
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    previous_id: Optional[str] = None
    """The last ID of the orders in the previous request."""
    limit: Optional[int] = None
    """Numbers of Orders
      顯示 n 筆訂單"""

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None
) -> AffiliateCampaignOrders:
    """
    Get Affiliate Campaign Orders
    
    To get affiliate campaign order.
    獲取使用特定推薦活動代碼的訂單。
    
    Path: GET /affiliate_campaigns/{id}/orders
    """
    # 构建请求 URL
    url = f"affiliate_campaigns/{id}/orders"

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
        return AffiliateCampaignOrders(**response_data)