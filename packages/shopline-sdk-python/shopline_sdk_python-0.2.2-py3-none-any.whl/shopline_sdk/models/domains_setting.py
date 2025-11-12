"""Shopline API 数据模型 - DomainsSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .domains_setting_webmaster import DomainsSettingWebmaster


class DomainsSetting(BaseModel):
    webmasters: Optional[DomainsSettingWebmaster] = None
    """Third Party Domain Tools   第三方網域工具"""