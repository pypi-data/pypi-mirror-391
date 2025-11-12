"""Shopline API 数据模型 - StorefrontTokenStaff"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class StorefrontTokenStaff(BaseModel):
    """The staff that created this storefront token 創建這令牌的商户"""
    id: Optional[str] = None
    """Staff ID 員工ID"""
    name: Optional[str] = None
    """Staff name 員工名稱"""
    email: Optional[str] = None
    """Staff email 員工電郵"""