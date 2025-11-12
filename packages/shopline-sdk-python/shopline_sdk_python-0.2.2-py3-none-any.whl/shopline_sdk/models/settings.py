"""Shopline API 数据模型 - Settings"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .app_setting import AppSetting
from .checkout_setting import CheckoutSetting
from .payments_setting import PaymentsSetting
from .pos_setting import PosSetting
from .product_review_setting import ProductReviewSetting
from .products_setting import ProductsSetting
from .promotions_setting import PromotionsSetting
from .tax_setting import TaxSetting
from .third_party_ads_setting import ThirdPartyAdsSetting
from .users_setting import UsersSetting


class Settings(BaseModel):
    users: Optional[UsersSetting] = None
    app: Optional[AppSetting] = None
    pos: Optional[PosSetting] = None
    products: Optional[ProductsSetting] = None
    checkout: Optional[CheckoutSetting] = None
    third_party_ads: Optional[ThirdPartyAdsSetting] = None
    tax: Optional[TaxSetting] = None
    payments: Optional[PaymentsSetting] = None
    product_review: Optional[ProductReviewSetting] = None
    promotions: Optional[PromotionsSetting] = None