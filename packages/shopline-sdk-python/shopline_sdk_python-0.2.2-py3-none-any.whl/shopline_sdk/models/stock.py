"""Shopline API 数据模型 - Stock"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Stock(BaseModel):
    warehouse_id: Optional[str] = None
    """Warehouse’s id 倉庫 id"""
    quantity: Optional[float] = None
    """Product’s stock in this warehouse 商品在此倉庫中的庫存"""