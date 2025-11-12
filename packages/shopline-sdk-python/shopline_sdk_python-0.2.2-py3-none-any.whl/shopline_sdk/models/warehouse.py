"""Shopline API 数据模型 - Warehouse"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Warehouse(BaseModel):
    id: Optional[str] = None
    """Warehouse’s id 倉庫 id"""
    name: Optional[str] = None
    """Warehouse’s name 倉庫名稱"""
    status: Optional[Union[Literal['active', 'transferring'], str]] = None
    """Warehouse’s status 倉庫狀態"""