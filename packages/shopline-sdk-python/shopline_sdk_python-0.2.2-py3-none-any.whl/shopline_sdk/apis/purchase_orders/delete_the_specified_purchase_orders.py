from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError

class Params(BaseModel):
    """查询参数模型"""
    ids: Optional[str] = Field(default=None, alias="ids[]")

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Dict[str, Any]:
    """
    Delete the specified purchase orders
    
    Delete the specified purchase orders
    批量刪除進貨單
    
    Path: PUT /pos/purchase_orders/bulk_delete
    """
    # 构建请求 URL
    url = "pos/purchase_orders/bulk_delete"

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
    async with session.put(
        url, params=query_params, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
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
        return response_data