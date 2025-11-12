from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.addon_product import AddonProduct
from shopline_sdk.models.paginatable import Paginatable

class Params(BaseModel):
    """查询参数模型"""
    previous_id: Optional[str] = None
    """The last ID of the addon products in the previous request.
      前一筆加購品的 ID 
      beta 測試中，僅開放部分店家使用，如無法使用功能請聯絡客服窗口"""
    id: Optional[str] = None
    """Addon Product ID
      加購品ID"""
    page: Optional[int] = None
    """Page
      頁數
      (Default: 1)"""
    per_page: Optional[int] = None
    """Numbers of Orders per page
      每頁顯示 n 筆資料
      (Default: 24, Max: 999)"""
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
      -
      *Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於
       quantity=100
       quantity=not:100
       quantity=lt:100
       quantity=lte:100
       quantity=gt:100
       quantity=gte:100"""
    updated_at: Optional[str] = None
    """Update Time
      更新時間
      -
      *Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於
       Example: "gt:2018-11-11 12:30:30" """
    created_at: Optional[str] = None
    """Created Time
      創建時間
      -
      *Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於
      
      Please fill in to the second level. Default value is 00:00:00 if only fill in dates.
      請輸入至秒數，若只輸入日期，則會自動帶入當天00:00:00"""
    include_fields: Optional[List[Union[Literal['promotions'], str]]] = Field(default=None, alias="include_fields[]")
    """Provide additional attributes in the response
      結果添加哪些參數"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[AddonProduct]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Search Addon Products
    
    To search add-on products with specific conditions.
    利用特殊條件搜尋加購品列表
    
    Path: GET /addon_products/search
    """
    # 构建请求 URL
    url = "addon_products/search"

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