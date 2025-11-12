"""Shopline API 数据模型 - PageSectionSettings"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .page_block_settings import PageBlockSettings



class Schema_SettingsConfig(BaseModel):
    """Configuration model for schema_settings"""
    settings: Optional[Dict[str, Union[str, float, int, bool, List[Any], Dict[str, Any]]]] = None
    """The settings of the schema Section的結構設定"""
    blocks: Optional[Dict[str, PageBlockSettings]] = None
    """The blocks included in the section Section內包含的blocks"""
    blocks_order: Optional[List[str]] = None
    """The blocks order in the section Section的blocks的排列次序"""

class PageSectionSettings(BaseModel):
    id: Optional[str] = None
    """The ID of the section defined by developer 由開發人員定義的Section ID"""
    type: Optional[Union[Literal['text', 'gallery', 'image-with-text', 'product-list', 'slideshow', 'product-list-slider'], str]] = None
    """The type of the section Section的類別"""
    schema_settings: Optional[Schema_SettingsConfig] = None
    """The schema of the section Section的結構"""
    children: Optional[List[str]] = None
    """The children of the section Section的子Section"""