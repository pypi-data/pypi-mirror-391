from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.not_found_error import NotFoundError

class Params(BaseModel):
    """查询参数模型"""
    locale_code: Optional[str] = None
    """Partner Locale Code"""

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None
) -> None:
    """
    Export Affiliate Campaign Report to Partner
    
    Send Affiliate Campaign to Partner
    
    Path: POST /affiliate_campaigns/{id}/export_report
    """
    # 构建请求 URL
    url = f"affiliate_campaigns/{id}/export_report"

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
    async with session.post(
        url, params=query_params, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            if response.status == 404:
                error = NotFoundError(**error_data)
                raise ShoplineAPIError(
                    status_code=404,
                    error=error
                )
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        # 无响应体，返回 None
        return None