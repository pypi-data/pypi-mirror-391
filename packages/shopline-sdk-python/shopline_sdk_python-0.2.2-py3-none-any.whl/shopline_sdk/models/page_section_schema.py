"""Shopline API 数据模型 - PageSectionSchema"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class PageSectionSchema(BaseModel):
    name: Optional[Translatable] = None
    tag: Optional[str] = None
    """Tag 標籤"""
    class_: Optional[str] = Field(default=None, alias="class")
    """Class 類別"""
    settings: Optional[List[Dict[str, Union[str, float, int, bool, List[Any], Dict[str, Any]]]]] = None
    """Settings details 設定詳情"""
    blocks: Optional[List[Dict[str, Union[str, float, int, bool, List[Any], Dict[str, Any]]]]] = None
    """Blocks details Blocks的詳情"""
    presets: Optional[List[Dict[str, Union[str, float, int, bool, List[Any], Dict[str, Any]]]]] = None
    """Presets details 預設詳情"""
    max_blocks: Optional[int] = None
    """Maximum number of blocks Blocks的最大值"""
    is_blocks_fixed: Optional[bool] = None
    """Whether the blocks are fixed Blocks是否被固定"""
    type: Optional[str] = None
    """The type of the page section schema. Page section schema的種類"""
    block_info: Optional[Translatable] = None
    icon: Optional[str] = None
    """Icon 頭像"""
    feature_key: Optional[str] = None
    """Feature key"""
    order: Optional[int] = None
    """Widget Ordering"""
    ui_options: Optional[Dict[str, Any]] = None
    """Ui options  Icon資訊"""