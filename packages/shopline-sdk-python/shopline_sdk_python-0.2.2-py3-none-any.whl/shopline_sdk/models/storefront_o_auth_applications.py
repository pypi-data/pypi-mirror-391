"""Shopline API 数据模型 - StorefrontOAuthApplications"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .storefront_o_auth_application import StorefrontOAuthApplication


class StorefrontOAuthApplications(BaseModel):
    items: Optional[List[StorefrontOAuthApplication]] = None