from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

class Params(BaseModel):
    """查询参数模型"""
    owner_id: str
    """owner id of the cart, could be user_id or public session id.
       購物車擁有者ID，登入會員的購物車此值是 user_id; 訪客的購物車則是 public_session_id"""
    owner_type: Union[Literal['User', 'Guest'], str]
    """owner type of the cart, could be User or Guest only.
       購物車擁有者類型，登入會員的購物車此值是 User; 訪客的購物車則是 Guest"""
    shop_session_id: Optional[str] = None
    """識別不同商務平台的直播購物車之 shop_session_id"""
    page_id: Optional[str] = None
    """一頁式商店 (express checkout)購物車的 page_id"""
    product_id: Optional[str] = None
    """快速結帳立即購買 (fast_checkout)購物車的 product_id"""
    channel_id: Optional[str] = None
    """購物車渠道 channel_id"""
    created_by: Optional[str] = None
    """購物車的建立來源"""

class Response(BaseModel):
    """响应体模型"""
    code: Optional[str] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get Cart Id
    
    To retrieve or generate a cart_id using cart identifiers.
     The cart_id remains valid until checkout is completed. If a cart is not found, a new one will be created.
     使用購物車識別欄位搜索或生成購物車 ID，購物車 ID在結帳完成前有效，若找不到對應的購物車，將自動創建新購物車
    
    Path: GET /carts/find
    """
    # 构建请求 URL
    url = "carts/find"

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