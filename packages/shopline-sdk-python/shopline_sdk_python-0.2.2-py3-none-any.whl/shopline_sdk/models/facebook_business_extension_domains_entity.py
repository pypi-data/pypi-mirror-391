"""Shopline API 数据模型 - FacebookBusinessExtensionDomainsEntity"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class FacebookBusinessExtensionDomainsEntity(BaseModel):
    id: Optional[str] = None
    """The ID of the owned domain object"""
    domain_name: Optional[str] = None
    """The domain name"""
    status: Optional[Union[Literal['verified', 'unverified'], str]] = None
    """indicating whether a domain is verified"""
    verfication_code: Optional[str] = None
    """The string token used to confirm domain"""