"""Shopline API 数据模型 - AppSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class AppSetting(BaseModel):
    appName: Optional[Dict[str, Any]] = None