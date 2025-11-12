from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.purchase_orders import PurchaseOrders
from shopline_sdk.models.server_error import ServerError

class Params(BaseModel):
    """查询参数模型"""
    query: Optional[str] = None
    """PurchaseOrder's number
      進貨單號碼"""
    type: Optional[str] = None
    """PurchaseOrder's type
      進貨單類型"""
    statuses: Optional[List[str]] = Field(default=None, alias="statuses[]")
    """PurchaseOrder's statuses
      進貨單狀態"""
    arrival_statuses: Optional[List[str]] = None
    """PurchaseOrder's arrival statuses
      進貨單到貨狀態"""
    channel_id: Optional[str] = None
    """PurchaseOrder's channel ID
      進貨單門市ID"""
    start_date: Optional[str] = None
    """PurchaseOrder's created at after date
      進貨單創建時間起始日"""
    end_date: Optional[str] = None
    """PurchaseOrder's created at before date
      進貨單創建時間終止日"""
    supplier_id: Optional[str] = None
    """PurchaseOrder's supplier ID
      進貨單供應商"""
    item_detail: Optional[bool] = None
    """Is PurchaseOrder's item detail required
      是否顯示進貨單項目細節"""

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> PurchaseOrders:
    """
    Get purchase orders
    
    Get purchase orders
    取得進貨單
    
    Path: GET /pos/purchase_orders
    """
    # 构建请求 URL
    url = "pos/purchase_orders"

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
        return PurchaseOrders(**response_data)