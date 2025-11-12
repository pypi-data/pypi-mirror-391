"""Shopline API 数据模型 - UpdateCategoryBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .category import Category
from .translatable import Translatable



class CategoryConfig(BaseModel):
    """Configuration model for category"""
    name_translations: Optional[Translatable] = None
    seo_title_translations: Optional[Translatable] = None
    seo_description_translations: Optional[Translatable] = None
    seo_keywords: Optional[str] = None
    seo_link: Optional[str] = None
    """SEO url 自訂SEO url"""
    parent_id: Optional[str] = None
    banner_url: Optional[str] = None
    """Category Banner Picture 分類横幅圖片"""
    priority: Optional[float] = None

class UpdateCategoryBody(BaseModel):
    """Payload for updating category"""
    category: Optional[CategoryConfig] = None