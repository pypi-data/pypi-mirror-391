from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.channel import Channel
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.server_error import ServerError

class Params(BaseModel):
    """查询参数模型"""
    include_fields: Optional[List[Union[Literal['e_invoice_setting', 'pin_codes'], str]]] = None
    """Some fields need to be specified in this parameter. Otherwise, it will not be returned.
       有些欄位需要定義在此參數內，否則將不會返回這些欄位的值。"""
    fields: Optional[List[Union[Literal['items.mobile_logo_media_url'], str]]] = None
    """For mobile logo media, need to add items.mobile_logo_media_url to this field.
       mobile logo media 必須加入 items.mobile_logo_media_url 到此欄位。"""

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None
) -> Channel:
    """
    Get Channel
    
    To get detailed information for a specific channel with its ID
    使用通路ID獲取特定一個通路的詳細資料
    
    Path: GET /channels/{id}
    """
    # 构建请求 URL
    url = f"channels/{id}"

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
        return Channel(**response_data)