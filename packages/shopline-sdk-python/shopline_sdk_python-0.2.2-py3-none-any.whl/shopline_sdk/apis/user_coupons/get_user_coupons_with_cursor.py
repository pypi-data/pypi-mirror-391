from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.user_coupons import UserCoupons

class Params(BaseModel):
    """查询参数模型"""
    promotion_id: str
    """Promotion ID"""
    next_cursor_id: Optional[str] = None
    """Next Cursor ID"""

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> UserCoupons:
    """
    Get User Coupons With Cursor
    
    Get User Coupons by Cursor
    獲取已領取的列表 By Cursor
    
    Path: GET /user_coupons/list
    """
    # 构建请求 URL
    url = "user_coupons/list"

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
        return UserCoupons(**response_data)