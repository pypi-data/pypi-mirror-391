from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.membership_tier import MembershipTier
from shopline_sdk.models.server_error import ServerError

class Params(BaseModel):
    """查询参数模型"""
    include_fields: Optional[List[Union[Literal['membership_tier_rules', 'member_point_rules', 'user_credit_rules', 'promotions'], str]]] = Field(default=None, alias="include_fields[]")
    """Provide additional attributes in the response
      結果添加哪些參數"""

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> List[MembershipTier]:
    """
    Get Membership Tiers
    
    To get membership tiers with open API
    獲取會員分級資料
    
    Path: GET /membership_tiers
    """
    # 构建请求 URL
    url = "membership_tiers"

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
        return [MembershipTier(**item) for item in response_data]