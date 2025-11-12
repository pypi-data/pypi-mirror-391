from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.layouts_setting import LayoutsSetting
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.server_error import ServerError

class Params(BaseModel):
    """查询参数模型"""
    exclude: Optional[List[str]] = None
    """Exclude the section to be published
      把此定元件從出版除外"""

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> LayoutsSetting:
    """
    Publish Layouts Setting
    
    To publish the setting of layouts
    出版佈局的設定
    
    Path: POST /settings/layouts/publish
    """
    # 构建请求 URL
    url = "settings/layouts/publish"

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
    async with session.post(
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
        return LayoutsSetting(**response_data)