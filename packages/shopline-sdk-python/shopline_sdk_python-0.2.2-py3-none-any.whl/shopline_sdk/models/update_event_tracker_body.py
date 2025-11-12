"""Shopline API 数据模型 - UpdateEventTrackerBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Config_DataConfig(BaseModel):
    """Configuration model for config_data"""
    tracking_code: str
    """Tracking code 追蹤碼"""
    access_token: str
    """Access token"""
    dynamic_remarketing: Optional[bool] = None
    """Dynamic Remarketing, specific for some kinds of event trackers."""
    single_variation: Optional[bool] = None
    """Single Variation, specific for some kinds of event trackers."""
    unique_ids: Optional[bool] = None
    """Unique IDs, specific for some kinds of event trackers."""

class UpdateEventTrackerBody(BaseModel):
    """Payload for updating an event tracker"""
    event_key: Union[Literal['tiktok', 'facebook_standard_pixel'], str]
    """The platform of tracking services. The event key must match with the existing record  追蹤平台。event_key 必須與現在的一致"""
    config_data: Config_DataConfig
    """Config data, each event_key has its own config  設定，每個event_key都有各自的config"""