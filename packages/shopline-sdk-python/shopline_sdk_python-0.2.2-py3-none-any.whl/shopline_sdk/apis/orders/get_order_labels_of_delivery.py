from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    ids: List[str] = Field(alias="ids[]")
    """Order ID
      訂單ID
      -
      Allow 24 order IDs in one batch
      一次最多輸入24筆訂單ID"""

class Response(BaseModel):
    """响应体模型"""
    fmt_b2c: Optional[List[str]] = None
    fmt_c2c: Optional[List[str]] = None
    seven_eleven_b2c: Optional[List[str]] = None
    tcat_roomtemp: Optional[List[str]] = None
    tcat_refrigerated: Optional[List[str]] = None
    tcat_frozen: Optional[List[str]] = None
    sfexpress: Optional[List[str]] = None
    sf_pickup: Optional[List[str]] = None
    hct_roomtemp: Optional[List[str]] = None
    hct_refrigerated: Optional[List[str]] = None
    hct_frozen: Optional[List[str]] = None
    failed_orders: Optional[Dict[str, List[Dict[str, Any]]]] = None

async def call(
    session: aiohttp.ClientSession, params: Optional[Params] = None
) -> Response:
    """
    Get Order Labels of Delivery
    
    To get delivery labels with order IDs.
    使用訂單ID獲取寄貨標籤。
     If validations are passed, those partially failed orders will be return, for *fmt_c2, fmt_b2, seven_eleven_b2c, tcat_roomtem, tcat_refrigerate, tcat_froze* orders.
     如果通過訂單資訊的驗證，如有部份*fmt_c2, fmt_b2, seven_eleven_b2c, tcat_roomtem, tcat_refrigerate, tcat_froze*單操作失敗， 部份失敗的訂單訊息將會被返回。
     The list of failed *fmt_c2, fmt_b2, seven_eleven_b2c, tcat_roomtem, tcat_refrigerate, tcat_froze*orders can be found from the *failed_orders* property. The property will be hidden if there are no errors.
     不成功的*fmt_c2, fmt_b2, seven_eleven_b2c, tcat_roomtem, tcat_refrigerate, tcat_froze* orders 將會出現在*failed_orders* 內。
    
    Path: GET /orders/label
    """
    # 构建请求 URL
    url = "orders/label"

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