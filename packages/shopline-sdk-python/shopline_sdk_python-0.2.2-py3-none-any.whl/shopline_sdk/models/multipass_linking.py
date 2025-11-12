"""Shopline API 数据模型 - MultipassLinking"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class MultipassLinking(BaseModel):
    customer_id: Optional[str] = None
    """Unique ID of customer"""
    sub: Optional[str] = None
    """Identifier given in multipass login token payload"""
    status: Optional[str] = None
    """status of linking, active means sub is valid for multipass login"""
    merchant_id: Optional[str] = None
    """Unique ID of merchant"""
    app_id: Optional[str] = None
    """Unique ID from app token payload"""
    updated_at: Optional[str] = None
    """Updated time 更新時間"""
    created_at: Optional[str] = None
    """Created time 建立時間"""