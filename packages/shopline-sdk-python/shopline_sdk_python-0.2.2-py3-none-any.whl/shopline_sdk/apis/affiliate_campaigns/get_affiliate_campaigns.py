from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.affiliate_campaigns import AffiliateCampaigns
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    active_status: Optional[Union[Literal['expired', 'ongoing'], str]] = None
    """The active status of affiliate campaign (expired or ongoing).
       推薦活動的狀態 (已過期或進行中)。"""
    partner_email: Optional[str] = None
    """The partner's email (To encode it with URI encode before sending)."""
    previous_id: Optional[str] = None
    """The last ID of the campaigns in the previous request. (for cursor base; empty is mean first page)
       前頁最後一筆編號(僅適用遊標取值，空值表示第一頁)"""
    page: Optional[int] = None
    """Page number (**Deprecated**)
      頁數(已過時不建議使用)"""
    per_page: Optional[int] = None
    """Numbers of channels per page
      每頁顯示資料筆數"""

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> AffiliateCampaigns:
    """
    Get Affiliate Campaigns
    
    To get affiliate campaigns.
    獲取推薦活動清單。
    
    Path: GET /affiliate_campaigns
    """
    # 构建请求 URL
    url = "affiliate_campaigns"

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
        return AffiliateCampaigns(**response_data)