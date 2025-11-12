from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.channel import Channel

class Params(BaseModel):
    """查询参数模型"""
    scope: Optional[Union[Literal['open_api', 'admin', 'shop_crm', 'pos', 'one', 'shoplytics', 'sc', 'dash', 'ads', 'payment_center', 'mc', 'form_builder'], str]] = None
    """The permissions scope
       獲取權限的範圍。
       If scope is not provided and the staff is the current merchant owner, no permissions will be returned. 
       如果沒有scope，而且管理員是店長，不會返回任何權限。"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Dict[str, Any]]] = None

async def call(
    session: aiohttp.ClientSession, id: Union[str], params: Optional[Params] = None
) -> Response:
    """
    Get staff permissions
    
    To retrieve permissions of a staff 
    獲取一個管理員的權限。
    
    Path: GET /staffs/{id}/permissions
    """
    # 构建请求 URL
    url = f"staffs/{id}/permissions"

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
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)