"""Shopline API 数据模型 - ThirdPartyAdsSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Facebook_Domain_VerificationConfig(BaseModel):
    """Configuration model for facebook_domain_verification"""
    api_response: Optional[Dict[str, Any]] = None


class FacebookConfig(BaseModel):
    """Configuration model for facebook"""
    business_id: Optional[str] = None
    fb_access_token: Optional[str] = None
    business_manager_id: Optional[str] = None
    commerce_merchant_settings_id: Optional[str] = None
    onsite_eligible: Optional[str] = None
    pixel_id: Optional[str] = None
    profiles: Optional[List[str]] = None
    ad_account_id: Optional[str] = None
    catalog_id: Optional[str] = None
    token_type: Optional[str] = None
    pages: Optional[List[str]] = None


class Adwords_DataConfig(BaseModel):
    """Configuration model for adwords_data"""
    adwords_enabled: Optional[str] = None
    credit_orders: Optional[List[Dict[str, Any]]] = None

class ThirdPartyAdsSetting(BaseModel):
    facebook_domain_verification: Optional[Facebook_Domain_VerificationConfig] = None
    facebook: Optional[FacebookConfig] = None
    """facebook ads setting"""
    adwords_data: Optional[Adwords_DataConfig] = None