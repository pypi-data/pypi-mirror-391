from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.product import Product
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    previous_id: Optional[str] = None
    """The last ID of the products in the previous request.
      前一筆商品的 ID 
      beta 測試中，僅開放部分店家使用，如無法使用功能請聯絡客服窗口"""
    sort_by: Optional[Union[Literal['asc', 'desc'], str]] = None
    """Setting sort by created time
      設定創建時間排序"""
    per_page: Optional[int] = None
    """Numbers of Products per page
      每頁顯示 n 筆資料"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    excludes: Optional[str] = Field(default=None, alias="excludes[]")
    """Could exclude certain parameters in the response
      結果要排除哪些參數"""
    fields: Optional[List[str]] = Field(default=None, alias="fields[]")
    """Could only show certain parameters in the response
      結果只顯示哪些參數"""
    id: Optional[str] = None
    """Only show specific products based on IDs
      結果只顯示哪些商品"""
    include_fields: Optional[List[Union[Literal['labels', 'metafields', 'bundle_set', 'type'], str]]] = Field(default=None, alias="include_fields[]")
    """Provide additional attributes in the response
      結果添加哪些參數"""
    with_product_set: Optional[bool] = None
    """Return product_set or not
      是否回傳組合商品"""
    updated_after: Optional[str] = None
    """Filter products by specific updated_after time.
      取得大於等於指定時間的商品
       *Should use UTC time'"""
    updated_before: Optional[str] = None
    """Filter products by specific updated_before time.
      取得小於等於指定時間的商品
       *Should use UTC time'"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Product]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get Products
    
    To get detailed information of couple products sorted by time
    利用時間範圍選取與排序獲取數筆商品資料
    
    Path: GET /products
    """
    # 构建请求 URL
    url = "products"

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