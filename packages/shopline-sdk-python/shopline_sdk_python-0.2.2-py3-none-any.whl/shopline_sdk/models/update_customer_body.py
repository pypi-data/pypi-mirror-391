"""Shopline API 数据模型 - UpdateCustomerBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .customer import Customer
from .order_delivery_address import OrderDeliveryAddress


class UpdateCustomerBody(BaseModel):
    """Payload for updating customer"""
    name: Optional[str] = None
    phones: Optional[List[str]] = None
    """Customer Phones 顧客電話 - *Not verified mobile phone number 請注意，非客戶手機驗證電話"""
    phone: Optional[str] = None
    """Customer's Phone 顧客電話 - *Not verified mobile phone number 請注意，非客戶手機驗證電話"""
    phone_country_code: Optional[str] = None
    """Customer Phone Country Code If phone is input, this field should not be blank  顧客電話國碼 手機號碼國碼, 如已輸入phone，此欄不能是空白"""
    gender: Optional[Union[Literal['male', 'female', 'other'], str]] = None
    birthday: Optional[str] = None
    birth_year: Optional[int] = None
    """Customer's birth year 顧客出生年份 -  *Could not be used with the birthday parameter at the same time."""
    birth_month: Optional[int] = None
    """Customer's birth month 顧客出生月份 -  *Could not be used with the birthday parameter at the same time."""
    birth_day: Optional[int] = None
    """Customer's birth day 顧客出生日期 -  *Could not be used with the birthday parameter at the same time."""
    email: Optional[str] = None
    """Customer Email 顧客電子郵件"""
    is_member: Optional[bool] = None
    is_blacklisted: Optional[bool] = None
    is_accept_marketing: Optional[bool] = None
    """Set as True for acceptance of marketing news. 是否接受優惠宣傳？"""
    is_subscribed_marketing_email: Optional[bool] = None
    """Set as True for acceptance of email marketing news. 是否接受email優惠宣傳？"""
    is_subscribed_marketing_sms: Optional[bool] = None
    """Set as True for acceptance of sms marketing news. 是否接受sms優惠宣傳？"""
    membership_tier_id: Optional[str] = None
    """Membership Tier ID 會員等級ID - Please check Get Membership Tiers"""
    tier_expires_at: Optional[str] = None
    """Tier Expires At 會員等級到期日 - Only future Date is available"""
    delivery_addresses: Optional[List[OrderDeliveryAddress]] = None
    """Customer's Delivery  顧客送貨地址 - *Maximum for 5 delivery address groups 最多五組"""
    ref_user_id: Optional[str] = None
    memo: Optional[str] = None
    tags: Optional[List[str]] = None
    """顧客標籤"""
    custom_fields: Optional[Dict[str, Any]] = None
    """Custom field content 顧客客製化欄位 - You can check  Get CustomFields  to get the custom_field_id, and parameter 可於 Get CustomFields  拿到客製化欄位的ID與參數"""
    registered_at: Optional[str] = None
    """Customer register's Date and time 顧客註冊時間"""
    locale_code: Optional[str] = None
    """Customer Locale Code 顧客使用前台之語言"""
    mobile_phone: Optional[str] = None
    """Customer Mobile Phone  It has to be used with mobile_phone_country_calling_code 顧客手機, 需與mobile_phone_country_calling_code一同使用"""
    mobile_phone_country_calling_code: Optional[str] = None
    """Country Code of Mobile Phone. It has to be used with mobile_phone  手機號碼國碼, 需與mobile_phone一同使用"""
    facebook_info: Optional[Dict[str, Any]] = None
    """Facebook info of the customer"""
    line_info: Optional[Dict[str, Any]] = None
    """Line info of the customer"""