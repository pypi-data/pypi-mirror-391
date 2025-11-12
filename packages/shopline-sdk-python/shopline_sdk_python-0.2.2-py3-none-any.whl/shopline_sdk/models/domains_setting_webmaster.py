"""Shopline API 数据模型 - DomainsSettingWebmaster"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class DomainsSettingWebmaster(BaseModel):
    google: Optional[str] = None
    """Google Search Console Google網站管理員工具"""
    bing: Optional[str] = None
    """Bing Webmaster Bing網站管理員工具"""
    facebook_domain_verification: Optional[str] = None
    """Facebook Domain Verification Facebook 網域驗證"""
    pinterest_domain_verification: Optional[str] = None
    """Pinterest Domain Verification Pinterest 網域驗證"""
    google_merchant_center: Optional[str] = None
    """Google Merchant Center Google Merchant Center"""
    google_merchant_id: Optional[str] = None
    """Google Merchant ID Google Merchant ID"""