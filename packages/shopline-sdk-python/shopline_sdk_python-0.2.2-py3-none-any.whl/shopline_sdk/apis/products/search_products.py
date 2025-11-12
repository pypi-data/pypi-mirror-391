from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.product import Product
from shopline_sdk.models.server_error import ServerError

class Params(BaseModel):
    """查询参数模型"""
    previous_id: Optional[str] = None
    """The last ID of the products in the previous request.
      前一筆商品的 ID 
      beta 測試中，僅開放部分店家使用，如無法使用功能請聯絡客服窗口"""
    page: Optional[int] = None
    """Page Number
      頁數（第n頁）"""
    per_page: Optional[int] = None
    """Numbers of Products per page
      每頁顯示 n 筆資料
       *If there're many products, it's suggested to set per_page number to 50
       如果商品眾多，建議per_page至多設定50"""
    query: Optional[str] = None
    """Support query order fields
      支援搜尋以下欄位
      product_name
      sku
      barcode"""
    id: Optional[str] = None
    """Product's ID
      商品ID
      Support equal, not equal and multiple search.
      支援 等於，不等於及多重搜尋"""
    category_id: Optional[str] = None
    """Categories
      分類
      *Accept category ids spilt by ","
      接受同時數個分類id，以","隔開"""
    status: Optional[Union[Literal['active', 'draft', 'removed', 'hidden'], str]] = None
    """Status
      商品狀態"""
    sort_type: Optional[Union[Literal['created_at', 'lowest_price', 'quantity_sold', 'custom_sorting'], str]] = None
    """Sort type. Default value is created_at."""
    sort_by: Optional[Union[Literal['desc', 'asc'], str]] = None
    """Sort order by sort_type. Default value is desc.
       When sort_type is 'quantity_sold', only 'desc' is allowed."""
    sku: Optional[str] = None
    """sku
      商品貨號
      Support equal, not equal and multiple search.
      支援 等於，不等於及多重搜尋"""
    barcode: Optional[str] = None
    """gtin
      商品條碼編號
      Support equal, not equal and multiple search.
      支援 等於，不等於及多重搜尋"""
    is_preorder: Optional[bool] = None
    """Is Preorder Product or not
      是否為預購商品"""
    quantity: Optional[str] = None
    """Quantity of Variation
      規格數量
       Support equal or not equal or less than or less than or equal or greater than or greater than or equal
       支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    variation_quantity: Optional[str] = None
    """Quantity of Variation
      規格數量
       Support equal or not equal or less than or less than or equal or greater than or greater than or equal
       支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    unlimited_quantity: Optional[bool] = None
    """Is Unlimited Quantity or not
      是否為無限數量"""
    created_at: Optional[str] = None
    """Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    updated_at: Optional[str] = None
    """Support equal or not equal or less than or  less than or equal or greater than or greater than or equal
      支援 等於 或 不等於 或 小於 或 小於等於 或 大於 或 大於等於"""
    title_translations: Optional[str] = None
    """Could search any match for all languages that merchant supported,
      可以搜出店家支援語系中的任何語系關鍵字"""
    summary_translations: Optional[str] = None
    """Could search any match for all languages that merchant supported,
      可以搜出店家支援語系中的任何語系關鍵字"""
    tags: Optional[str] = None
    """Product Tag
      產品標籤"""
    excludes: Optional[str] = Field(default=None, alias="excludes[]")
    """Could exclude certain parameters in the response
      結果要排除哪些參數"""
    fields: Optional[str] = Field(default=None, alias="fields[]")
    """Could only show certain parameters in the response
      結果只顯示哪些參數"""
    include_fields: Optional[List[Union[Literal['labels'], str]]] = Field(default=None, alias="include_fields[]")
    """Provide additional attributes in the response
      結果添加哪些參數"""
    retail_status: Optional[Union[Literal['active', 'draft'], str]] = None
    """POS Status
      POS商品上架狀態"""
    with_product_set: Optional[bool] = None
    """Search with Product Set
      是否包含組合商品"""
    purchasable: Optional[bool] = None
    """Is Purchasable Set
      是否可購買"""
    allow_gift: Optional[bool] = None
    """Specifies whether the item can be set as a gift.
       是否可以設為贈品
       true: the product can be set as a gift.
       false: the product cannot be set as a gift."""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Product]] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Search Products
    
    To search products with specific conditions.
    利用特殊條件搜尋商品列表。
    
    Path: GET /products/search
    """
    # 构建请求 URL
    url = "products/search"

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