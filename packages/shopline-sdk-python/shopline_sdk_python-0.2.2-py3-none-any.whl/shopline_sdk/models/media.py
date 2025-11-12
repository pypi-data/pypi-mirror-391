"""Shopline API 数据模型 - Media"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class Media(BaseModel):
    id: Optional[str] = None
    """Media ID"""
    alt_translations: Optional[Translatable] = None
    images: Optional[Dict[str, Any]] = None
    """Object contains url of image in different dimensions 包含不同大小圖片的連絡"""