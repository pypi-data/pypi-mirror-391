"""Shopline API 数据模型 - CreateBulkOperationBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .product import Product
from .translatable import Translatable



class DataItem(BaseModel):
    """Item model for data"""
    operation_ref_id: str
    """The id of the product 商品ID"""
    product: Dict[str, Any]

class CreateBulkOperationBody(BaseModel):
    """Payload for creating bulk operation"""
    data: Optional[List[DataItem]] = None
    """Bulk operation payload.  創建新商品批量操作所需內容。"""