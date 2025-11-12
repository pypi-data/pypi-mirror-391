"""Shopline API 数据模型 - Staff"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Owned_MerchantsItem(BaseModel):
    """Item model for owned_merchants"""
    id: Optional[str] = None
    """Merchant ID"""
    name: Optional[str] = None
    """Merchant name"""
    handle: Optional[str] = None
    """Merchant handle"""
    base_country_code: Optional[str] = None
    """Merchant country code"""
    custom_domain: Optional[str] = None
    """Merchant custom domain"""


class Employed_MerchantsItem(BaseModel):
    """Item model for employed_merchants"""
    id: Optional[str] = None
    """Merchant ID"""
    name: Optional[str] = None
    """Merchant name"""
    handle: Optional[str] = None
    """Merchant handle"""
    base_country_code: Optional[str] = None
    """Merchant country code"""
    custom_domain: Optional[str] = None
    """Merchant custom domain"""

class Staff(BaseModel):
    id: Optional[str] = None
    """ID"""
    email: Optional[str] = None
    """Email 電郵"""
    name: Optional[str] = None
    """Name 員工名稱"""
    locale_code: Optional[str] = None
    """Locale of staff using 員工語系"""
    owned_merchants: Optional[List[Owned_MerchantsItem]] = None
    """Associated merchants this staff owns 帳號為店長的店鋪"""
    employed_merchants: Optional[List[Employed_MerchantsItem]] = None
    """Associated merchants this staff belongs to 帳號服務的店鋪"""
    user_id: Optional[str] = None
    """user ID 使用者 ID"""
    created_at: Optional[str] = None
    """Created Time 創建時間"""
    merchant_ids: Optional[List[str]] = None
    """Associated merchant IDs this staff belongs to 帳號服務的店鋪 ID"""
    organization_ids: Optional[List[str]] = None
    """Associated organization IDs this staff belongs to 帳號服務的組織 ID"""
    role_keys: Optional[List[str]] = None
    profile_image_url: Optional[str] = None
    """Profile image url  個人資料相片URL"""
    channel_ids: Optional[List[str]] = None
    """Channel IDs  頻道 IDs"""