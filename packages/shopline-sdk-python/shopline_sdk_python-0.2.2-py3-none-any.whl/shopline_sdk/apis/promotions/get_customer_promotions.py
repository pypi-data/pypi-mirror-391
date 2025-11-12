from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.customer_promotion import CustomerPromotion

class Params(BaseModel):
    """查询参数模型"""
    coupon_status: Optional[Union[Literal['valid', 'invalid', 'comingSoon'], str]] = None
    """優惠券狀態"""
    available_platforms: Optional[List[Union[Literal['ec', 'retail'], str]]] = None
    """優惠券適用渠道"""
    coupon_type: Optional[List[Union[Literal['draw', 'single', 'multi'], str]]] = None
    """優惠券形式"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[CustomerPromotion]] = None

async def call(
    session: aiohttp.ClientSession, customer_id: str, params: Optional[Params] = None
) -> Response:
    """
    Get Customer Promotions
    
    To get customer promotions
    取得用戶優惠活動
    
    Path: GET /customers/{customer_id}/promotions
    """
    # 构建请求 URL
    url = f"customers/{customer_id}/promotions"

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