"""Shopline API 数据模型 - AddressPreferenceLayoutData"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class AddressPreferenceLayoutData(BaseModel):
    """Display location of the single address data value 單一地址資料的顯示位置"""
    row: Optional[int] = None
    """The number of row 列"""
    column: Optional[int] = None
    """The number of column 欄"""
    width: Optional[int] = None
    """Width of display 寬度"""