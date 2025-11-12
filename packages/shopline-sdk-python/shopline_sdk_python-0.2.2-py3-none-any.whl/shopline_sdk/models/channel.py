"""Shopline API 数据模型 - Channel"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable



class PhonesConfig(BaseModel):
    """Configuration model for phones"""
    main: Optional[str] = None


class Pin_CodesItem(BaseModel):
    """Item model for pin_codes"""
    code: Optional[str] = None
    scope: Optional[str] = None


class E_Invoice_SettingConfig(BaseModel):
    """Configuration model for e_invoice_setting"""
    invoice_type: Optional[Union[Literal['none', 'tradevan', 'cetustek'], str]] = None
    """invoice setting type"""
    invoice: Optional[Dict[str, Any]] = None
    """only show this object when invoice_type is cetustek"""
    invoice_tradevan: Optional[Dict[str, Any]] = None
    """only show this object when invoice_type is tradevan"""

class Channel(BaseModel):
    id: Optional[str] = None
    name: Optional[Translatable] = None
    platform: Optional[Union[Literal['Shopee', 'shop_crm', 'online', 'pos', 'sc'], str]] = None
    """Shopee  shop_crm  online  pos  sc"""
    merchant_id: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None
    currency_code: Optional[str] = None
    merchant_name: Optional[str] = None
    default_warehouse_id: Optional[str] = None
    identifier: Optional[str] = None
    phones: Optional[PhonesConfig] = None
    address: Optional[Dict[str, Any]] = None
    pin_codes: Optional[List[Pin_CodesItem]] = None
    mobile_logo_media_url: Optional[str] = None
    e_invoice_setting: Optional[E_Invoice_SettingConfig] = None
    """only expose this object when the request_params include_fields contains e_invoice_setting value and the merchant of the channel has sl_pos_one_einvoice_setting rollout_key"""