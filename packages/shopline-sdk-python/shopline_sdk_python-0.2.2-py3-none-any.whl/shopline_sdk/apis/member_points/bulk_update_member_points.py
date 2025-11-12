from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    user_ids: List[str]
    """List of user IDs to update. 
       user ID 的列表，指定要更新的 user"""
    value: float
    """The value to set for each user's member points. 
       要給予每個 user 的點數數量"""
    remarks: str
    """Remarks for the member points update. 
       點數更新的備註"""
    performer_id: Optional[str] = None
    """The ID of the performer making the update. Optional. 
       執行者 ID"""
    email_target: Optional[float] = None
    """Allowed 1 & 3. 1 means not send, 3 means send all. 
       電子郵件是否發送，1為不發送，3為發送"""
    sms_notification_target: Optional[float] = None
    """Allowed 1~3. 1 means not send, 2 means send with verified, 3 means send all. 
       簡訊是否發送通知，1為不發送，2為發送至驗證手機，3為全部發送"""

class Response(BaseModel):
    """响应体模型"""
    message: Optional[str] = None
    job_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> Response:
    """
    Bulk Update Member Points
    
    Bulk update multiple user member points records. 
     批量更新多個 users 點數
    
    Path: POST /member_points/bulk_update
    """
    # 构建请求 URL
    url = "member_points/bulk_update"

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
        return Response(**response_data)