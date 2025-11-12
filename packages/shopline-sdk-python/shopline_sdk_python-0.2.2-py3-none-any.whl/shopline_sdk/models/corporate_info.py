"""Shopline API 数据模型 - CorporateInfo"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class AddressConfig(BaseModel):
    """Configuration model for address"""
    zip_code: Optional[str] = None
    """Postal code 郵遞區號"""
    address_line: Optional[str] = None
    """Address line 地址"""
    district: Optional[str] = None
    """District name 區"""
    district_code: Optional[str] = None
    """District code 區代碼"""
    city: Optional[str] = None
    """City name 城市"""
    city_code: Optional[str] = None
    """City code 城市代碼"""

class CorporateInfo(BaseModel):
    name: Optional[str] = None
    """Company name 公司名稱"""
    identity_number: Optional[str] = None
    """Unified Business Number 統一編號"""
    responsible_person_first_name: Optional[str] = None
    """Responsible person's first name 負責人名字"""
    responsible_person_last_name: Optional[str] = None
    """Responsible person's last name 負責人姓氏"""
    address: Optional[AddressConfig] = None
    """Company address 公司地址"""