from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    id: Optional[str] = None
    """Wish List Item ID
      追蹤清單項目ID"""
    customer_id: Optional[str] = None
    """Customer ID
      顧客 ID"""
    product_id: Optional[str] = None
    """Product ID
      商品ID"""
    variation_key: Optional[str] = None
    """Product's variation's key
      商品規格key
       If product does not have variations, please set to empty string.
      若商品無規格，請填入空字串"""

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Dict[str, Any]:
    """
    Delete Wish List Item
    
    To delete wish list item with open API
    刪除追蹤清單
    
    Path: DELETE /wish_list_items
    """
    # 构建请求 URL
    url = "wish_list_items"

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
    async with session.delete(
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
        return response_data