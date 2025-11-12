from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.customer_coupon_promotions import CustomerCouponPromotions

class Params(BaseModel):
    """查询参数模型"""
    promotion_ids: List[str]
    """優惠活動 ID"""

async def call(
    session: aiohttp.ClientSession, customer_id: str, params: Optional[Params] = None
) -> CustomerCouponPromotions:
    """
    Get Customer Coupon Promotions
    
    To get customer coupon promotions with promotion_ids.
     The API returns promotions only if the given promotions whose type are draw.
     And it returns the promotions which are available to draw or have already been drawn.
     It returns null if the given promotions are not available.
    
     使用 promotion_ids 獲取用戶優惠活動。
     此 API 只會回傳傳入的 promotion_ids 中，類型為領取型的優惠活動，並僅回傳已領取或可領取的優惠動。
     若傳入的 promotion_ids 中有不可領取的優惠活動，則該優惠活動會回傳 null。
    
    Path: GET /customers/{customer_id}/coupon_promotions
    """
    # 构建请求 URL
    url = f"customers/{customer_id}/coupon_promotions"

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
        return CustomerCouponPromotions(**response_data)