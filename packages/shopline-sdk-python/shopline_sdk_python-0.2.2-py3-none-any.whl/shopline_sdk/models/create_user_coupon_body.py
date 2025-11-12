"""Shopline API 数据模型 - CreateUserCouponBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class User_CouponConfig(BaseModel):
    """Configuration model for user_coupon"""
    customer_id: Optional[str] = None
    promotion_id: Optional[str] = None

class CreateUserCouponBody(BaseModel):
    """Payload for creating user coupon"""
    user_coupon: User_CouponConfig
    mail_notify: Optional[bool] = None
    sms_notify: Optional[bool] = None