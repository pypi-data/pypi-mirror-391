"""Shopline API 数据模型 - Tax"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .tax_region import TaxRegion



class SalesConfig(BaseModel):
    """Configuration model for sales"""
    general: Optional[TaxRegion] = None
    details: Optional[List[Union[TaxRegion]]] = None


class DeliveryConfig(BaseModel):
    """Configuration model for delivery"""
    general: Optional[TaxRegion] = None
    details: Optional[List[Union[TaxRegion]]] = None


class Service_ChargeConfig(BaseModel):
    """Configuration model for service_charge"""
    general: Optional[TaxRegion] = None
    details: Optional[List[Union[TaxRegion]]] = None

class Tax(BaseModel):
    id: Optional[str] = None
    """ID"""
    name: Optional[str] = None
    """name"""
    merchant_id: Optional[str] = None
    """merchant ID"""
    country: Optional[str] = None
    """Country of the tax 稅收國家/地區"""
    is_default_rates: Optional[bool] = None
    """Using default tax rates 自動計算稅率"""
    enable_inclusive: Optional[bool] = None
    """All products' price include tax 所有商品皆已含稅"""
    allow_inclusive_tax: Optional[bool] = None
    """Allow inclusive_tax 國家商品允許含稅"""
    service_charge_taxable: Optional[bool] = None
    """Service charge taxable 服務稅應稅"""
    emoji_flag: Optional[str] = None
    """emoji flag 國家emoji"""
    sales: Optional[SalesConfig] = None
    """tax of sales 基本消費稅"""
    delivery: Optional[DeliveryConfig] = None
    """tax of delivery 運費稅"""
    service_charge: Optional[Service_ChargeConfig] = None
    """Tax of service charge 服務稅"""
    created_at: Optional[str] = None
    """Created Date 稅收創造時間 (UTC +0)"""
    updated_at: Optional[str] = None
    """Created Date 稅收更新時間 (UTC +0)"""