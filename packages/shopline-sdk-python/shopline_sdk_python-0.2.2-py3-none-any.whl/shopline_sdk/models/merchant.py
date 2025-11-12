"""Shopline API 数据模型 - Merchant"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .media import Media
from .merchant_tax import MerchantTax



class Whitelisted_Ip_AddressesItem(BaseModel):
    """Item model for whitelisted_ip_addresses"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: Optional[str] = None
    address: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None

class Merchant(BaseModel):
    id: Optional[str] = None
    """Merchant ID 商户ID"""
    base_country_code: Optional[str] = None
    """Country/Region code 國家/地區代碼"""
    base_currency_code: Optional[str] = None
    """Currency code 貨幣代碼"""
    name: Optional[str] = None
    """Shop Name 商店名稱"""
    email: Optional[str] = None
    """Shop Email 商店電郵"""
    handle: Optional[str] = None
    """Shop code 商店代碼"""
    custom_domain: Optional[str] = None
    """Shop custom domain 商店自訂網域"""
    current_plan_key: Optional[str] = None
    """Shop plan key 商店計劃代碼"""
    default_language_code: Optional[str] = None
    """Default language code 默認語言代碼"""
    staff_id: Optional[str] = None
    """Staff ID 管理員ID"""
    rollout_keys: Optional[List[str]] = None
    """Supported function keys 支援的功能代碼"""
    supported_languages: Optional[List[str]] = None
    """Supported languages 支援的語言"""
    logo_media: Optional[Media] = None
    kyc_status: Optional[Union[Literal['not_yet_applied', 'basic_account_pending', 'basic_account_verified', 'basic_account_rejected', 'basic_account_reviewed', 'advanced_account_pending', 'advanced_account_verified', 'advanced_account_rejected', 'advanced_account_failed'], str]] = None
    """KYC status KYC審核狀態"""
    admin_status: Optional[Union[Literal['normal', 'suspended'], str]] = None
    """Admin status"""
    sl_payment_merchant_id: Optional[str] = None
    """sl_payment_merchant_id 支付中台merchant id"""
    sl_payment_mcc: Optional[str] = None
    """sl_payment_mcc 渠道分配的mcc"""
    sl_payment_billing_descriptor_name: Optional[str] = None
    """Store's billing descriptor 商店交易名稱"""
    product_lines: Optional[Dict[str, Any]] = None
    """Product Lines 商戶訂閱"""
    tags: Optional[List[str]] = None
    """tags 標籤"""
    emails: Optional[Dict[str, Any]] = None
    """emails 其他電郵"""
    phones: Optional[Dict[str, Any]] = None
    """phones 電話"""
    pos_payment_id: Optional[str] = None
    """POS payment id"""
    pos_delivery_option_id: Optional[str] = None
    """POS Delivery option id"""
    brand_home_url: Optional[str] = None
    """Storefront url 店鋪地址"""
    taxes: Optional[List[MerchantTax]] = None
    """Tax Info of Merchant 商店稅金設定"""
    current_theme_key: Optional[str] = None
    """The theme key that the merchant is currently 商家當前正在使用的主題  Only provided when include_fields contains 'current_theme_key'  僅於include_fields傳入 'current_theme_key' 時提供"""
    instagram_username: Optional[str] = None
    """The instagram username of the merchant linked currently 商家當前正在連結的Instagram用戶名稱  Only provided when include_fields contains 'instagram_username'  僅於include_fields傳入 'instagram_username' 時提供"""
    whitelisted_ip_addresses: Optional[List[Whitelisted_Ip_AddressesItem]] = None
    """The whitelisted IP addresses  登入 IP 位置白名單  Presented in GET /merchants/:merchant_id, but not in GET /merchants  會於 GET /merchants/:merchant_id，但不於 GET /merchants 出現"""