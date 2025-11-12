"""Shopline API 数据模型 - AddressNode"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class AddressNode(BaseModel):
    """Address node 地址節點"""
    id: Optional[str] = None
    """Address node ID 地址節點 ID"""
    country_id: Optional[str] = None
    """Country ID 國家ID"""
    level: Optional[int] = None
    """Address node level 地址節點層級"""
    parent_address_node_id: Optional[str] = None
    """Parent address node ID 父層地址節點ID"""
    name_translations: Optional[Translatable] = None
    zip_code: Optional[str] = None
    """Postcode 郵遞區號"""
    code: Optional[str] = None
    """地址節點代碼"""
    address_nodes: Optional[List['AddressNode']] = None
    """Children address node 子層地址節點"""