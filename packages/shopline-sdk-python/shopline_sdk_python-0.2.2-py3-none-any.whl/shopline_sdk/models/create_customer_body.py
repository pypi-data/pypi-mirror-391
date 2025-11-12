"""Shopline API 数据模型 - CreateCustomerBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .customer import Customer
from .order_delivery_address import OrderDeliveryAddress


class CreateCustomerBody(BaseModel):
    """Payload for updating customer"""
    name: Optional[str] = None
    email: Optional[str] = None
    """Customer's Email 顧客電子郵件 - *Customers will receive a requirement to reset password by email after creation. 使用open api Create Customer之後顧客將會收到要求重新設定密碼之email"""
    mobile_phone: Optional[str] = None
    """Customer Mobile Phone, separate by comma if multiple  It has to be used with mobile_phone_country_calling_code 顧客手機, 以逗號分隔, 需與mobile_phone_country_calling_code一同使用"""
    mobile_phone_country_calling_code: Optional[str] = None
    """Country Code of Mobile Phone. It has to be used with mobile_phone  It has to be comply with the "Mobile sign up country" in customer setting 手機號碼國碼, 需與mobile_phone一同使用  號碼所屬國家需符合後台設定的「手機註冊支援國家」"""
    send_notification: Optional[bool] = None
    """Will send welcome email/sms if True 是否發出歡迎電郵/短訊 -- Default: true"""
    notification_types: Optional[List[Union[Literal['email', 'sms'], str]]] = None
    """Email and/or SMS.  SMS can be sent only after enabling feature.  System will try to send both email and SMS if this field is not specified.  電郵 及/或 短訊。  需開通功能後才能發出短訊。  如漏空，系統會嘗試所有通知方法"""
    phones: Optional[str] = None
    """Customer's Phones 顧客電話 - *Not verified mobile phone number 請注意，非客戶手機驗證電話"""
    phone: Optional[str] = None
    """Customer's Phone 顧客電話 - *Not verified mobile phone number 請注意，非客戶手機驗證電話"""
    phone_country_code: Optional[str] = None
    """Customer Phone Country Code.<br />顧客電話國碼"""
    gender: Optional[Union[Literal['male', 'female', 'other'], str]] = None
    birthday: Optional[str] = None
    birth_year: Optional[int] = None
    """Customer's birth year 顧客出生年份 -  *Could not be used with the birthday parameter at the same time."""
    birth_month: Optional[int] = None
    """Customer's birth month 顧客出生月份 -  *Could not be used with the birthday parameter at the same time."""
    birth_day: Optional[int] = None
    """Customer's birth day 顧客出生日期 -  *Could not be used with the birthday parameter at the same time."""
    is_member: Optional[bool] = None
    """Set as True for registered customer 是否為會員？"""
    is_accept_marketing: Optional[bool] = None
    """Set as True for acceptance of marketing news. 是否接受優惠宣傳？"""
    is_subscribed_marketing_email: Optional[bool] = None
    """Set as True for acceptance of email marketing news. 是否接受email優惠宣傳？"""
    is_subscribed_marketing_sms: Optional[bool] = None
    """Set as True for acceptance of sms marketing news. 是否接受sms優惠宣傳？"""
    delivery_addresses: Optional[List[OrderDeliveryAddress]] = None
    """Customer's Delivery Address 顧客送貨地址 - *Maximum for 5 delivery address groups 最多五組"""
    is_allow_welcome_credit: Optional[bool] = None
    """Set as True for sending welcome credit. 是否發送入會購物金  *If welcome credit is enabled at admin panel, welcome credit and notification will be sent when creating customer. 若後台啟用入會購物金功能，建立顧客時會發送入會購物金與通知  Default: false"""
    created_by: Optional[Union[Literal['shop', 'admin', 'openapi', 'shop_crm', 'pos'], str]] = None
    """Creation source 記錄創建來源"""
    created_by_channel_id: Optional[str] = None
    """Creation source id 記錄創建來源的id"""
    registered_by: Optional[Union[Literal['shop', 'admin', 'openapi', 'shop_crm', 'pos'], str]] = None
    """Registration source 會員註冊來源"""
    registered_by_channel_id: Optional[str] = None
    """Registration source id 會員註冊來源的id"""
    memo: Optional[str] = None
    tags: Optional[List[str]] = None
    """顧客標籤"""
    membership_tier_id: Optional[str] = None
    """Membership Tier ID The details of the Membership Tier could be retrieved from Get Membership Tiers endpoint  會員等級ID 會員等級的詳細資料可在Get Membership Tiers的endpoint檢索到"""