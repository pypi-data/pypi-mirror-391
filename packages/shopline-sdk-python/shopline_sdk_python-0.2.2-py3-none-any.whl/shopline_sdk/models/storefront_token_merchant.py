"""Shopline API 数据模型 - StorefrontTokenMerchant"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class StorefrontTokenMerchant(BaseModel):
    """The merchant that this storefront token can access 這令牌能存取的商户"""
    id: Optional[str] = None
    """Merchant ID 商户ID"""
    name: Optional[str] = None
    """Merchant name 商户名稱"""
    email: Optional[str] = None
    """Merchant email 商户電郵"""
    handle: Optional[str] = None
    """Merchant handle 商户handle"""