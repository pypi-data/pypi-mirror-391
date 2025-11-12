"""Shopline API 数据模型 - OrderCustomerInfo"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable



class Custom_DataItem(BaseModel):
    """Item model for custom_data"""
    value: Optional[str] = None
    name_translations: Optional[Translatable] = None
    field_id: Optional[str] = None

class OrderCustomerInfo(BaseModel):
    gender: Optional[str] = None
    """Gender 性別"""
    birthday: Optional[str] = None
    """Birthday 生日"""
    custom_data: Optional[List[Custom_DataItem]] = None
    """Custom Fields 客製化欄位"""