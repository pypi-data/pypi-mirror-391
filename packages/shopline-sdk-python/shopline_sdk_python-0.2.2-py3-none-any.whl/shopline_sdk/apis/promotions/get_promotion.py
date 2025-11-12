from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.promotion import Promotion

class Params(BaseModel):
    """查询参数模型"""
    show_whitelisted_membership_tier: Optional[bool] = None
    """Response whitelisted MembershipTier Data
      回傳指定會員資料"""
    show_summary: Optional[bool] = None
    """Respone Promotion Summary
      回傳優惠活動概覽"""

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None
) -> Promotion:
    """
    Get Promotion
    
    To get detailed information for a specific promotion with its ID
    使用優惠活動ID獲取特定一個優惠活動的詳細資料
    
    Path: GET /promotions/{id}
    """
    # 构建请求 URL
    url = f"promotions/{id}"

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
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Promotion(**response_data)