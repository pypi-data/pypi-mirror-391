from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.category import Category
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.server_error import ServerError

class Params(BaseModel):
    """查询参数模型"""
    previous_id: Optional[str] = None
    """The last ID of the addon products in the previous request.
      前一筆分類的 ID 
      beta 測試中，僅開放部分店家使用，如無法使用功能請聯絡客服窗口"""
    updated_after: Optional[str] = None
    """Filter categories by those updated after specific time.
      取得 updated_at 大於指定時間的分類(包含指定時間)
       *Should use UTC time'"""
    updated_before: Optional[str] = None
    """Filter categories by those updated before specific time.
      取得 updated_at 小於指定時間的分類(包含指定時間)
       *Should use UTC time'"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    per_page: Optional[int] = None
    """Numbers of Orders per Page
      每頁顯示 n 筆資料"""
    excludes: Optional[List[str]] = Field(default=None, alias="excludes[]")
    """Could exclude certain parameters in the response
      結果要排除哪些參數"""
    fields: Optional[List[str]] = Field(default=None, alias="fields[]")
    """Could only show certain parameters in the response
      結果只顯示哪些參數"""
    created_by_filter: Optional[Union[Literal['admin', 'pos'], str]] = None
    """Filter categories by those created by. Default 'admin'. 
      取得指定 created_by 的分類。預設為'admin'。"""
    with_product_set: Optional[bool] = None
    """Include product set in response. Default false.
      是否在回應中包含商品集。預設為false。"""
    include_fields: Optional[List[str]] = Field(default=None, alias="include_fields[]")
    """Provide additional attributes in the response
      結果添加哪些參數"""
    category_ids: Optional[List[str]] = Field(default=None, alias="category_ids[]")
    """The category ids to be included in the response
      結果包含哪些分類"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[Category]] = None
    pagination: Optional[Paginatable] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get Categories
    
    To get detailed information of couple categories sorted by time
    利用時間範圍選取與排序獲取分類資料
    
    Path: GET /categories
    """
    # 构建请求 URL
    url = "categories"

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