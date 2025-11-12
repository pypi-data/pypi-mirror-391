from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.paginatable import Paginatable
from shopline_sdk.models.product_review_comments import ProductReviewComments
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    previous_id: Optional[str] = None
    """The last ID of the product review comments in the previous request.
      前一筆商品評價的 ID 
      beta 測試中，僅開放部分店家使用，如無法使用功能請聯絡客服窗口"""
    product_id: Optional[str] = None
    """Product id
      產品id"""
    page: Optional[int] = None
    """Page Number
      頁數"""
    per_page: Optional[int] = None
    """Numbers of items per Page
      每頁顯示 n 筆資料"""
    sort_by: Optional[Union[Literal['created_at', 'score'], str]] = None
    """Sorting by field
      以欄位排序"""
    order_by: Optional[Union[Literal['asc', 'desc'], str]] = None
    """Setting sort by created time
      設定排序"""
    status: Optional[str] = None
    """Status
      狀態"""

class Response(BaseModel):
    """响应体模型"""
    items: Optional[List[ProductReviewComments]] = None
    pagination: Optional[Paginatable] = None
    last_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get Product Review Comments
    
    To retrieve product review comments.
    抓取商品評價。
    
    Path: GET /product_review_comments
    """
    # 构建请求 URL
    url = "product_review_comments"

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
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Response(**response_data)