"""Shopline API 数据模型 - CreateEventTrackerBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Config_DataConfig(BaseModel):
    """Configuration model for config_data"""
    tracking_code: Optional[str] = None
    """Tracking code 追蹤碼"""
    access_token: Optional[str] = None
    """Access token"""

class CreateEventTrackerBody(BaseModel):
    """Payload for creating an event tracker"""
    event_key: Union[Literal['tiktok', 'facebook_standard_pixel'], str]
    """The platform of tracking services 追蹤平台"""
    event_type: Union[Literal['loaded_home_page', 'added_product_to_cart', 'loaded_checkout_page', 'placed_an_order', 'loaded_any_page'], str]
    """The event to be tracked 需要追蹤的事件"""
    config_data: Config_DataConfig
    """Config data, each event_key has its own config  設定，每個event_key都有各自的config"""