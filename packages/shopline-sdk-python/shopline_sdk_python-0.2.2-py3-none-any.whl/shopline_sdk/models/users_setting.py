"""Shopline API 数据模型 - UsersSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .member_point_rule import MemberPointRule
from .user_credit_rule import UserCreditRule



class Line_LoginConfig(BaseModel):
    """Configuration model for line_login"""
    status: Optional[Union[Literal['active', 'inactive'], str]] = None
    """line login active status"""


class Facebook_LoginConfig(BaseModel):
    """Configuration model for facebook_login"""
    status: Optional[Union[Literal['active', 'inactive'], str]] = None
    """facebook login enable status"""
    app_id: Optional[str] = None
    """facebook app id"""
    app_secret: Optional[str] = None
    """facebook app_secret"""
    client_token: Optional[str] = None
    """facebook client_token"""


class Enable_Facebook_CommentConfig(BaseModel):
    """Configuration model for enable_facebook_comment"""
    status: Optional[bool] = None
    """facebook comment enable status"""


class Email_VerificationConfig(BaseModel):
    """Configuration model for email_verification"""
    status: Optional[str] = None
    """email verification enable status"""


class Email_Login_With_VerificationConfig(BaseModel):
    """Configuration model for email_login_with_verification"""
    status: Optional[str] = None
    """email login verification enable status"""


class Sms_VerificationConfig(BaseModel):
    """Configuration model for sms_verification"""
    status: Optional[str] = None
    """mobile_phone verification enable status"""
    supported_countries: Optional[List[str]] = None
    """mobile_phone support countries"""

class UsersSetting(BaseModel):
    birthday_format: Optional[Union[Literal['YYYY/MM/DD', 'YYYY/MM', 'MM/DD'], str]] = None
    """The birthday format of the user (default: "YYYY/MM/DD")  會員生日格式（預設："YYYY/MM/DD"）"""
    send_birthday_credit_period: Optional[Union[Literal['monthly', 'daily'], str]] = None
    """The birthday credit sending setting of the user (default: "daily")  會員生日點數發送時間（預設："daily"為當日, "monthly"為當月一號）"""
    line_login: Optional[Line_LoginConfig] = None
    facebook_login: Optional[Facebook_LoginConfig] = None
    enable_facebook_comment: Optional[Enable_Facebook_CommentConfig] = None
    pos_apply_credit: Optional[bool] = None
    pos_apply_member_point: Optional[bool] = None
    user_credit_rules: Optional[List[UserCreditRule]] = None
    member_point_rules: Optional[List[MemberPointRule]] = None
    minimum_age_limit: Optional[str] = None
    """The minimum age required for customers to shop at the online store 在網店購物的年齡下限  minimum: "13"  最小: "13"  maximum: "130"  最大: "130" """
    enable_member_point: Optional[bool] = None
    """Whether the member point rules are activated  會員點數規則是否正在生效"""
    enable_user_credit: Optional[bool] = None
    """Store Credits Toggle 商店購物金總開關"""
    enable_age_policy: Optional[bool] = None
    """Age Policy Toggle 是否開啟顧客已滿年齡同意文案"""
    email_verification: Optional[Email_VerificationConfig] = None
    """Require customer email verification 是否開啟顧客電郵驗證"""
    email_login_with_verification: Optional[Email_Login_With_VerificationConfig] = None
    """Customer login requrie email verification 是否開啟顧客完成電郵驗證後才可能入"""
    sms_verification: Optional[Sms_VerificationConfig] = None
    """Require customer sms verification 是否開啟顧客手機驗證"""
    signup_method: Optional[Union[Literal['email', 'mobile', 'email_and_mobile'], str]] = None
    """Customer signup method 顧客註冊方式"""