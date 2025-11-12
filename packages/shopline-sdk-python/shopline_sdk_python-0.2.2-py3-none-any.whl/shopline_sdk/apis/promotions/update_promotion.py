from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.promotion import Promotion
from shopline_sdk.models.update_promotion_body import UpdatePromotionBody as Body

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> Promotion:
    """
    Update Promotion
    
    To update detailed information of couple promotions
    更新優惠活動 
    
    <strong> * Cannot update the conditions </strong> 
    Updating promotion condition requires the condition id . 
    Providing the condition id will <strong>NOT</strong> update the condition. 
    <strong> Need endpoints for create and update condition.</strong> 
    <strong> * 不能更新活動條件 </strong> 
    更新活動的條件須要 condition id. 
    但提供 condition id <strong>不會</strong> 更新條件的值。 
    <strong> 需要建立和更新 條件 的功能。 </strong>
    
    Path: PUT /promotions/{id}
    """
    # 构建请求 URL
    url = f"promotions/{id}"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.put(
        url, json=json_data, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return Promotion(**response_data)