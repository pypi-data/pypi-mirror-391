"""Shopline API 数据模型 - PosSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class PosSetting(BaseModel):
    mobile_logo_media_url: Optional[str] = None
    terms_and_condition: Optional[str] = None
    show_title: Optional[bool] = None
    show_original_price: Optional[bool] = None
    show_footer_image: Optional[bool] = None
    apply_platform: Optional[str] = None
    footer_image_media_url: Optional[str] = None