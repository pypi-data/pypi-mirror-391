from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

class Response(BaseModel):
    """响应体模型"""
    message: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, id: str
) -> Response:
    """
    Delete Promotion
    
    To delete promotion with open API
    透過open API刪除優惠活動
    
    Path: DELETE /promotions/{id}
    """
    # 构建请求 URL
    url = f"promotions/{id}"

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