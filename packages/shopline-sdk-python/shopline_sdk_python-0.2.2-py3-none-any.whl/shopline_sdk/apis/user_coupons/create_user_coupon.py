from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.create_user_coupon_body import CreateUserCouponBody as Body

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> None:
    """
    Create User Coupon
    
    To create user coupon
    創建優惠券
    
    Path: POST /user_coupons
    """
    # 构建请求 URL
    url = "user_coupons"

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
        # 无响应体，返回 None
        return None