"""Shopline API 数据模型 - CreateMetafieldDefinitionBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .metafield_definition import MetafieldDefinition
from .metafield_value import MetafieldValue


class CreateMetafieldDefinitionBody(BaseModel):
    """Payload for creating metafield definition"""
    namespace: Optional[str] = None
    key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    field_type: Optional[Union[Literal['single_line_text_field', 'multi_line_text_field', 'number_integer', 'number_decimal', 'json', 'boolean', 'url'], str]] = None