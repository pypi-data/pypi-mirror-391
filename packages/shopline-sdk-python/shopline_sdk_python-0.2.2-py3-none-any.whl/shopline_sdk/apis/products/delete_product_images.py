from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

class Body(BaseModel):
    """请求体模型"""
    media_ids: Optional[List[str]] = None
    """Ids of the Images
      需要被刪除圖片的IDs"""

class Response(BaseModel):
    """响应体模型"""
    result: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> Response:
    """
    Delete Product Images
    
    To delete product images with open API
    透過open API刪除主商品圖片/商品資訊圖片
    
    
    Path: DELETE /products/{id}/delete_images
    """
    # 构建请求 URL
    url = f"products/{id}/delete_images"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.delete(
        url, json=json_data, headers=headers
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