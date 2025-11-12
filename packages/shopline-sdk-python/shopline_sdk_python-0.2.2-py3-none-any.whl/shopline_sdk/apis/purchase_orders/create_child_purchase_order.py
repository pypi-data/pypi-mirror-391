from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.purchase_order import PurchaseOrder
from shopline_sdk.models.server_error import ServerError


class PurchaseOrderSchema(BaseModel):
    """Model for purchase_order"""
    scheduled_time: Optional[str] = None
    issuer_id: str

class Body(BaseModel):
    """请求体模型"""
    purchase_order: Optional[PurchaseOrderSchema] = None

async def call(
    session: aiohttp.ClientSession, PurchaseOrderId: str, body: Optional[Body] = None
) -> PurchaseOrder:
    """
    Create child purchase order
    
    Create child purchase order
    建立子進貨單
    
    Path: POST /pos/purchase_orders/{PurchaseOrderId}/child
    """
    # 构建请求 URL
    url = f"pos/purchase_orders/{PurchaseOrderId}/child"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.post(
        url, json=json_data, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
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
        return PurchaseOrder(**response_data)