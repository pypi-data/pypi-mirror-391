from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

class Response(BaseModel):
    """响应体模型"""
    result: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, id: str
) -> Response:
    """
    Delete Flash Price Campaign
    
    To delete a flash price campaign
    刪除商品限時促銷價活動
    
    Path: DELETE /flash_price_campaigns/{id}
    """
    # 构建请求 URL
    url = f"flash_price_campaigns/{id}"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.delete(
        url, headers=headers
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
        return Response(**response_data)