from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.cart import Cart

class Params(BaseModel):
    """查询参数模型"""
    calculate_all: Optional[bool] = None
    """To calculate info for checkout usage, only turn this option on when you ready to checkout.
       用於計算結帳相關資訊，僅在準備結帳時啟用此選項"""

class Response(BaseModel):
    """响应体模型"""
    code: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Cart] = None
    trace_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None
) -> Response:
    """
    Get Cart
    
    To get cart information by inputting cart id
     以購物車ID取得該購物車資料
    
    Path: GET /carts/{id}
    """
    # 构建请求 URL
    url = f"carts/{id}"

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