"""Shopline API 数据模型 - Translatable"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Translatable(BaseModel):
    en: Optional[str] = None
    """Merchant defined English name 店家定義英文名稱"""
    zh_hant: Optional[str] = Field(default=None, alias="zh-hant")
    """Merchant defined Traditional Chinese name 店家定義繁體中文名稱"""
    zh_cn: Optional[str] = Field(default=None, alias="zh-cn")
    """Merchant defined Simplified Chinese name 店家定義簡體中文名稱"""
    vi: Optional[str] = None
    """Merchant defined Vietnamese name 店家定義越南文名稱"""
    ms: Optional[str] = None
    """Merchant defined Malaysian name 店家定義馬來西亞文名稱"""
    ja: Optional[str] = None
    """Merchant defined Japanese name 店家定義日文名稱"""
    th: Optional[str] = None
    """Merchant defined Thai name 店家定義泰文名稱"""
    id: Optional[str] = None
    """Merchant defined Indian name 店家定義印度文名稱"""
    de: Optional[str] = None
    """Merchant defined Deutsch name 店家定義德文名稱"""
    fr: Optional[str] = None
    """Merchant defined France name 店家定義法文名稱"""