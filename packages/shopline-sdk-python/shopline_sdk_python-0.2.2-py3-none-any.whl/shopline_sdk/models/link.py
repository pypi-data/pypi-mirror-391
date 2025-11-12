"""Shopline API 数据模型 - Link"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable



class Seo_ImageConfig(BaseModel):
    """Configuration model for seo_image"""
    id: Optional[str] = None
    """Media ID"""
    url: Optional[str] = None
    """Media URL"""

class Link(BaseModel):
    id: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    name_translations: Optional[Translatable] = None
    value_id: Optional[str] = None
    url_link: Optional[str] = None
    key: Optional[str] = None
    html_target: Optional[str] = None
    section: Optional[str] = None
    owner_id: Optional[str] = None
    parent_id: Optional[str] = None
    priority: Optional[float] = None
    children_ids: Optional[List[str]] = None
    created_at: Optional[str] = None
    """Created Time 建立時間"""
    updated_at: Optional[str] = None
    """Updated Time 更新時間"""
    seo_image: Optional[Seo_ImageConfig] = None
    """SEO Image SEO社群預覽圖"""