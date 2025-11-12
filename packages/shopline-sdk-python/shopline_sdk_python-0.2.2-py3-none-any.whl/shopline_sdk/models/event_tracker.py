"""Shopline API 数据模型 - EventTracker"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Config_DataConfig(BaseModel):
    """Configuration model for config_data"""
    dynamic_remarketing: Optional[bool] = None
    """false by default"""
    single_variation: Optional[bool] = None
    """false by default"""
    unique_ids: Optional[bool] = None
    """false by default"""
    tracking_code: Optional[str] = None
    """tracking code"""
    access_token: Optional[str] = None
    """for tiktok"""

class EventTracker(BaseModel):
    id: Optional[str] = None
    """ID"""
    event_type: Optional[Union[Literal['loaded_home_page', 'added_product_to_cart', 'loaded_checkout_page', 'placed_an_order', 'loaded_any_page'], str]] = None
    event_key: Optional[Union[Literal['tiktok', 'facebook_standard_pixel'], str]] = None
    """The platform of tracking services"""
    status: Optional[Union[Literal['active'], str]] = None
    """The status of the event tracker"""
    created_at: Optional[str] = None
    """created time"""
    updated_at: Optional[str] = None
    """updated time"""
    config_data: Optional[Config_DataConfig] = None
    """Config data, each event has its own config key"""