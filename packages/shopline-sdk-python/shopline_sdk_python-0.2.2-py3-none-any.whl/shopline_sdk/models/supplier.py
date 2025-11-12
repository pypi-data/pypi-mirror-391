"""Shopline API 数据模型 - Supplier"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class Supplier(BaseModel):
    id: Optional[str] = None
    """Id of the supplier 供應商ID"""
    name_translations: Optional[Translatable] = None
    name: Optional[str] = None
    """Name of the supplier 供應商名稱"""
    address: Optional[str] = None
    """Address of the supplier 供應商地址"""
    phone: Optional[str] = None
    """Phone of the supplier 供應商電話號碼"""
    note: Optional[str] = None
    """Note of the supplier 供應商備注"""
    status: Optional[str] = None
    """Working status of the supplier 供應商狀態 (active/removed)"""