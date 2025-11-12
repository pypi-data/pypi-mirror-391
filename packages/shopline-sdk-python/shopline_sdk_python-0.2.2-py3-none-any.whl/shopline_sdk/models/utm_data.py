"""Shopline API 数据模型 - UtmData"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class UtmData(BaseModel):
    utm_source: Optional[str] = None
    """UTM Source 標識哪個站點發送了流量，並且是必填參數。"""
    utm_campaign: Optional[str] = None
    """UTM Campaign 標識特定的產品促銷或戰略活動。"""
    utm_medium: Optional[str] = None
    """UTM Medium 標識所使用的鏈接類型，例如每次點擊或電子郵件的費用。"""
    utm_content: Optional[str] = None
    """UTM Content 標識用於將用戶帶到網站的具體操作，例如橫幅廣告或文本鏈接。 它通常用於A / B測試和以內容定位的廣告。 textlink logolink"""
    utm_term: Optional[str] = None
    """UTM Term 標識搜索詞。"""
    utm_time: Optional[str] = None
    """UTM Time"""