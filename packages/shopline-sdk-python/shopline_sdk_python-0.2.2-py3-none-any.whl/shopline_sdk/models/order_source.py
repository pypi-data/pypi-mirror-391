"""Shopline API 数据模型 - OrderSource"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class OrderSource(BaseModel):
    id: Optional[str] = None
    """ID of the order source 訂單來源ID"""
    type: Optional[Union[Literal['storefront', 'offline_store', 'offline_store_other', 'fb', 'fb_other', 'shopline_live', 'line', 'shopee', 'whatsapp', 'lazada', 'instagram', 'zalo', 'phone', 'email', 'other'], str]] = None
    """Type of the order source 訂單來源類型"""
    source_id: Optional[str] = None
    """ID of the external source 外部來源id  Might be fb_fan_page_id / channel_id 可能是 fb_fan_page_id / channel_id"""
    name: Optional[Dict[str, Any]] = None
    """Name 名字  Might be fb fan page name / channel name 可能是 fb 粉絲頁面名稱/頻道名稱"""