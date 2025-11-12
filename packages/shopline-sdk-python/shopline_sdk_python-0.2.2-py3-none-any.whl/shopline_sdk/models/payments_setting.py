"""Shopline API 数据模型 - PaymentsSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Deep_LinkConfig(BaseModel):
    """Configuration model for deep_link"""
    ios: Optional[Dict[str, Any]] = None
    """ios 平台的深層連結跳轉設定"""
    android: Optional[Dict[str, Any]] = None
    """android 平台的深層連結跳轉設定"""

class PaymentsSetting(BaseModel):
    deep_link: Optional[Deep_LinkConfig] = None