from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.order_comment import OrderComment
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Body(BaseModel):
    """请求体模型"""
    text: Optional[str] = None
    """The message of the comment
      該退貨單通訊的訊息內容"""
    media_id: Optional[str] = None
    """The id of the media
      該退貨單通訊的媒體id"""
    is_private: Optional[bool] = None
    """The type of the comment. 
       If true, the message can only be viewed by the shop admin.
       If false, the message can also be viewed by the customer.
       訂單通訊的類型。若為true，則該訂單通訊只能被網店管理查看。
       若為false，則顧客也可查看。目前只開放給網店管理查看。"""
    send_by: Optional[Union[Literal['merchant'], str]] = None
    """The message sender
      該訂單通訊的發送者"""
    trackable_type: Optional[str] = None
    trackable_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> OrderComment:
    """
    Create Return Order Message (Not Available Yet)
    
    To create an return order note
    創建退貨單備註
    
    Path: POST /return_orders/{id}/messages
    """
    # 构建请求 URL
    url = f"return_orders/{id}/messages"

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
        return OrderComment(**response_data)