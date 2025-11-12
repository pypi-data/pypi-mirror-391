from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

class Body(BaseModel):
    """请求体模型"""
    customer_id: Optional[str] = None
    channel_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, couponCode: str, body: Optional[Body] = None
) -> Dict[str, Any]:
    """
    Redeem User Coupon
    
    To redeem user coupon
    核銷優惠券
    
    Path: POST /user_coupons/{couponCode}/redeem
    """
    # 构建请求 URL
    url = f"user_coupons/{couponCode}/redeem"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.post(
        url, json=json_data, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()
        return response_data