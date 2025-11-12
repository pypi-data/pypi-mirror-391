"""Shopline API 数据模型 - ThemeSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .product_related_theme_settings import ProductRelatedThemeSettings


class ThemeSetting(BaseModel):
    enabled_quick_cart: Optional[bool] = None
    opens_in_new_tab: Optional[bool] = None
    enabled_sort_by_sold: Optional[bool] = None
    buy_now_button: Optional[Dict[str, Any]] = None
    plp_wishlist: Optional[bool] = None