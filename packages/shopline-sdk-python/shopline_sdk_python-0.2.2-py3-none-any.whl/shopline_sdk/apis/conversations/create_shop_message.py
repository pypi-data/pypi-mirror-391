from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.shop_conversation import ShopConversation
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError


class RefDataSchema(BaseModel):
    """Model for ref_data"""
    path: Optional[str] = None
    full_path: Optional[str] = None

class Body(BaseModel):
    """请求体模型"""
    text: Optional[str] = None
    """The text of the message
      訊息內容"""
    media_id: Optional[str] = None
    """The id of the media
      訊息媒體id"""
    sender_id: Optional[str] = None
    """The message sender ID
      訊息發送者ID"""
    sender_email: Optional[str] = None
    """The message sender email
      訊息發送者email"""
    recipient_id: Optional[str] = None
    """The message recipient ID
      訊息接收者ID"""
    ref_data: Optional[RefDataSchema] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> ShopConversation:
    """
    Create Shop Message
    
    To create shop messages
    創建商店訊息
    
    Path: POST /conversations/message
    """
    # 构建请求 URL
    url = "conversations/message"

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
        return ShopConversation(**response_data)