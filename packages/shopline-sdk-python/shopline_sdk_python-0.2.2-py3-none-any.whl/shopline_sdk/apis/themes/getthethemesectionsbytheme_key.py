from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.theme_schema import ThemeSchema
from shopline_sdk.models.unauthorized_error import UnauthorizedError

class Params(BaseModel):
    """查询参数模型"""
    template_key: Optional[str] = None
    """Template Key"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[ThemeSchema] = None

async def call(
    session: aiohttp.ClientSession, theme_key: str, params: Optional[Params] = None
) -> Response:
    """
    Get the theme sections by theme_key
    
    To get the page sections of the theme with the theme_key
    用theme_key請求該主題有的頁面sections
    
    Path: GET /themes/{theme_key}/sections
    """
    # 构建请求 URL
    url = f"themes/{theme_key}/sections"

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
            if response.status == 401:
                error = UnauthorizedError(**error_data)
                raise ShoplineAPIError(
                    status_code=401,
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