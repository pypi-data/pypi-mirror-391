from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.customer import Customer
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unauthorized_error import UnauthorizedError

class Params(BaseModel):
    """查询参数模型"""
    excludes: Optional[List[str]] = Field(default=None, alias="excludes[]")
    """Exclude certain parameters in the response
      結果要排除哪些參數"""
    fields: Optional[List[Union[Literal['membership_tier_gap'], str]]] = Field(default=None, alias="fields[]")
    """Only show certain parameters in the response
       This field will have conflicts to the include_fields[]
       To avoid the conflicts
       please also input all the items included in the include_fields[] to this field
       otherwise those fields will not be shown
       結果只顯示哪些參數
       這個欄位會跟include_fields[]的欄位有衝突
       要避免衝突的話，請輸入所有也包括在include_fields[]內的項目
       否則那些項目將不能被顯示"""
    include_fields: Optional[List[Union[Literal['metafields'], str]]] = Field(default=None, alias="include_fields[]")
    """Provide additional attributes in the response
      結果添加哪些參數"""

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None
) -> Customer:
    """
    Get Customer
    
    To get detailed information for a specific customer with its ID
    使用顧客ID獲取特定一個顧客的詳細資料
    
    Path: GET /customers/{id}
    """
    # 构建请求 URL
    url = f"customers/{id}"

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
            if response.status == 401:
                error = UnauthorizedError(**error_data)
                raise ShoplineAPIError(
                    status_code=401,
                    error=error
                )
            if response.status == 404:
                error = NotFoundError(**error_data)
                raise ShoplineAPIError(
                    status_code=404,
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
        return Customer(**response_data)