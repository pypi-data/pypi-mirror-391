from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.member_point import MemberPoint
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unauthorized_error import UnauthorizedError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    value: int
    """Points to be added or deducted
      增加或減除點數
      -
      *Number can be -999999~999999"""
    remarks: str
    """Reason for adding or deducting member points
      增加或減除點數原因
      -
      *Limit to max 50 characters"""
    email_target: Optional[int] = None
    """Notification with Email
      是否發送email通知
      Only applicable for addition
      僅適用於增加
      -
       1=NOT_SEND全部不送
       3=SEND_TO_ALL全部都送"""
    sms_notification_target: Optional[int] = None
    """Notification with SMS
      是否發送簡訊通知
      Only applicable for addition
      僅適用於增加
      -
       1=NOT_SEND全部不送
       2=SEND_VERIFIED只送手機驗證過的
       3=SEND_TO_ALL全部都送"""
    performer_id: Optional[str] = None
    """Performer ID
      操作者ID"""
    performer_type: Optional[Union[Literal['User', 'Agent'], str]] = None
    """Performer Type
      操作者類型"""

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> MemberPoint:
    """
    Update Customer Member Points
    
    Using open API to update customer member points
    
    Path: POST /customers/{id}/member_points
    """
    # 构建请求 URL
    url = f"customers/{id}/member_points"

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
            if response.status == 401:
                error = UnauthorizedError(**error_data)
                raise ShoplineAPIError(
                    status_code=401,
                    error=error
                )
            if response.status == 404:
                error = NotFoundError(**error_data)
                raise ShoplineAPIError(
                    status_code=404,
                    error=error
                )
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
        return MemberPoint(**response_data)