"""Shopline API 数据模型 - UpdateAppMetafieldBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .app_metafield_value import AppMetafieldValue


class UpdateAppMetafieldBody(BaseModel):
    """Payload for updating metafield"""
    field_type: Optional[Union[Literal['single_line_text_field', 'multi_line_text_field', 'number_integer', 'number_decimal', 'json', 'boolean', 'url'], str]] = None
    field_value: Optional[Union[str, float, bool, Dict[str, Any]]] = None