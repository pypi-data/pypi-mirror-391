"""Shopline API 数据模型 - Category"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable



class Banner_MediasItem(BaseModel):
    """Item model for banner_medias"""
    image: Optional[Dict[str, Any]] = None
    id: Optional[str] = Field(default=None, alias="_id")
    alt_translations: Optional[Dict[str, Any]] = None
    link: Optional[Dict[str, Any]] = None
    new_tab: Optional[Dict[str, Any]] = None

class Category(BaseModel):
    id: Optional[str] = None
    """Category ID 分類ID"""
    name_translations: Optional[Translatable] = None
    seo_title_translations: Optional[Translatable] = None
    seo_description_translations: Optional[Translatable] = None
    seo_keywords: Optional[str] = None
    """SEO Keyword SEO 關鍵字"""
    key: Optional[str] = None
    """Special category 特殊分類鍵"""
    sort_setting: Optional[str] = None
    """sort setting 排序設定"""
    status: Optional[Union[Literal['active', 'removed'], str]] = None
    """Status 狀態"""
    banner_medias: Optional[List[Banner_MediasItem]] = None
    """Banner Medias 分類橫圖"""
    parent_id: Optional[str] = None
    """Parent Category ID 母分類ID"""
    priority: Optional[float] = None
    """Weight to control sorting 分類權重"""
    created_by: Optional[Union[Literal['admin', 'pos'], str]] = None
    """Created By 創造來自"""
    children: Optional[List[Dict[str, Any]]] = None
    """Array of Sub Categories Information 子分類資訊序列"""
    product_count: Optional[int] = None
    """Product count, only available for /v1/categories with  params include_fields[] have value 'product_count'  商品數目, 只適用於連同參數 include_fields[] 等於 'product_count' 時呼叫 /v1/categories"""