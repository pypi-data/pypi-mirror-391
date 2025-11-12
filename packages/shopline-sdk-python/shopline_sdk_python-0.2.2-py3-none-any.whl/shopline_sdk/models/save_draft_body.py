"""Shopline API 数据模型 - SaveDraftBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .link import Link
from .page import Page
from .page_section_settings import PageSectionSettings
from .translatable import Translatable


class SaveDraftBody(BaseModel):
    """Payload for creating page"""
    type: Optional[str] = None
    title_translations: Optional[Translatable] = None
    content_translations: Optional[Translatable] = None
    seo_title_translations: Optional[Translatable] = None
    seo_description_translations: Optional[Translatable] = None
    seo_keywords: Optional[str] = None
    link: Optional[Link] = None
    use_noindex_meta_tag: Optional[bool] = None
    sections: Optional[Dict[str, PageSectionSettings]] = None
    sections_order: Optional[List[str]] = None