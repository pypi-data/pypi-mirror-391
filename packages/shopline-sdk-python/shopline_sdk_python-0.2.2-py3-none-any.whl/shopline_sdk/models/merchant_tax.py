"""Shopline API 数据模型 - MerchantTax"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .tax_region import TaxRegion



class SalesConfig(BaseModel):
    """Configuration model for sales"""
    general: Optional[TaxRegion] = None
    details: Optional[List[TaxRegion]] = None


class DeliveryConfig(BaseModel):
    """Configuration model for delivery"""
    general: Optional[TaxRegion] = None
    details: Optional[List[TaxRegion]] = None


class Service_ChargeConfig(BaseModel):
    """Configuration model for service_charge"""
    general: Optional[TaxRegion] = None
    details: Optional[List[TaxRegion]] = None

class MerchantTax(BaseModel):
    id: Optional[str] = None
    """Tax ID 稅金設定ID"""
    name: Optional[str] = None
    """Tax Name 稅金名稱"""
    merchant_id: Optional[str] = None
    """Merchant ID 商户ID"""
    country: Optional[str] = None
    """country code 國家代碼"""
    is_default_rates: Optional[bool] = None
    """is use default rates or not 是否是預設稅率"""
    enable_inclusive: Optional[bool] = None
    """is enable inclusive or not 商品是否含稅"""
    allow_inclusive_tax: Optional[bool] = None
    """is allow to enable inclusive tax or not 是否允許商品含稅"""
    service_charge_taxable: Optional[bool] = None
    """is service charge taxable or not  服務稅是否應稅"""
    emoji_flag: Optional[str] = None
    """emoji of country flag 國旗emoji"""
    sales: Optional[SalesConfig] = None
    delivery: Optional[DeliveryConfig] = None
    service_charge: Optional[Service_ChargeConfig] = None