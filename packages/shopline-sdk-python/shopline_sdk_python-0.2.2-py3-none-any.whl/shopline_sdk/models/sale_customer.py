"""Shopline API 数据模型 - SaleCustomer"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Customer_InfoConfig(BaseModel):
    """Configuration model for customer_info"""
    name: Optional[str] = None
    """Customer Name 顧客姓名"""
    email: Optional[str] = None
    """Customer Email 顧客電子郵件"""
    phone: Optional[str] = None
    """Customer Phone 顧客電話"""
    mobile_phone: Optional[str] = None
    """Customer Mobile Phone 顧客手機"""

class SaleCustomer(BaseModel):
    post_sales_user_id: Optional[str] = None
    """Customer ID in live stream 直播間顧客 ID"""
    platform: Optional[str] = None
    """Live Platform 直播渠道"""
    social_user_id: Optional[str] = None
    """Third-party media user ID 第三方平台的顧客 ID  FB/Group: PSID  IG: IGSID  LINE: 未綁定 EC 會員: EC Customer ID; 已綁定 EC 會員: line_uid  Shopline: EC Customer Id"""
    has_customer_bind: Optional[bool] = None
    """是否綁定會員"""
    customer_id: Optional[str] = None
    """EC Customer ID EC 顧客 ID"""
    customer_info: Optional[Customer_InfoConfig] = None