from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.event_trackers import EventTrackers
from shopline_sdk.models.not_found_error import NotFoundError

class Params(BaseModel):
    """查询参数模型"""
    version: Optional[str] = None
    """控制 api version"""

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None
) -> EventTrackers:
    """
    Get an Event Tracker
    
    To get detailed information for a specific event tracker with its ID
     使用事件追蹤ID獲取特定第三方事件追蹤的詳細資料
    
    Path: GET /event_trackers/{id}
    """
    # 构建请求 URL
    url = f"event_trackers/{id}"

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
        response_data = await response.json()

        # 验证并返回响应数据
        return EventTrackers(**response_data)