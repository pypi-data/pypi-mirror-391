"""Shopline API 数据模型 - ShopSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class ShopSetting(BaseModel):
    home_page: Optional[str] = None
    page_schedules: Optional[List[Any]] = None