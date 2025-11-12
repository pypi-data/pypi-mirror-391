"""Shopline API 数据模型 - StorefrontOAuthApplication"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class StorefrontOAuthApplication(BaseModel):
    id: Optional[str] = None
    """Application ID"""
    app_id: Optional[str] = None
    """App UID (Client ID used in OAuth requests)"""
    app_secret: Optional[str] = None
    """App Secret (Client secret used in OAuth requests)"""
    name: Optional[str] = None
    """App Name"""
    redirect_uri: Optional[str] = None
    """Redirect URI"""