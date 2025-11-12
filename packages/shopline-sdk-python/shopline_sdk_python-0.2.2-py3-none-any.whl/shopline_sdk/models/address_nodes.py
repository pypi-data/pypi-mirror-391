"""Shopline API 数据模型 - AddressNodes"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .address_node import AddressNode
from .translatable import Translatable


class AddressNodes(BaseModel):
    id: Optional[str] = None
    """Country ID 國家ID"""
    code: Optional[str] = None
    """Country code 國碼"""
    name_translations: Optional[Translatable] = None
    address_nodes_count: Optional[int] = None
    """Address node count 地址節點總數"""
    address_nodes: Optional[List[AddressNode]] = None