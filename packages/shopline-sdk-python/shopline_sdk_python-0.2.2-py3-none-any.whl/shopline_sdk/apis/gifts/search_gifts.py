from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.gift import Gift
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    previous_id: Optional[str] = None
    """The last ID of the gifts in the previous request.
      前一筆贈品的 ID 
      beta 測試中，僅開放部分店家使用，如無法使用功能請聯絡客服窗口"""
    id: Optional[str] = None
    """Gift's ID
      贈品 ID"""
    page: Optional[int] = None
    """Page Number
      頁數（第n頁）"""
    per_page: Optional[int] = None
    """Numbers of Gifts per page
      每頁顯示 n 筆資料"""
    status: Optional[Union[Literal['active', 'draft'], str]] = None
    """Status
      商品狀態"""
    sort_by: Optional[Union[Literal['desc', 'asc'], str]] = None
    """Sort by created_at"""
    sku: Optional[str] = None
    """SKU
      貨物編號"""
    quantity: Optional[str] = None
    """Quantity
      數量
       Support equal or not equal or less than or less than or equal or greater than or greater than or equal
       支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    updated_at: Optional[str] = None
    """Updated Time
      更新時間
       Support equal or not equal or less than or less than or equal or greater than or greater than or equal
       支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    created_at: Optional[str] = None
    """Created Time
      創建時間"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Gift]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Search Gifts
    
    To search gifts with specific conditions.
    利用特殊條件搜尋贈品列表。
    
    Path: GET /gifts/search
    """
    # 构建请求 URL
    url = "gifts/search"

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