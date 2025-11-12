"""Shopline API 数据模型 - ProductRelatedThemeSettings"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Buy_Now_ButtonConfig(BaseModel):
    """Configuration model for buy_now_button"""
    enabled: Optional[bool] = None

class ProductRelatedThemeSettings(BaseModel):
    enabled_quick_cart: Optional[bool] = None
    """Show "Instant Add to Cart" Button in the Store or not.  是否在前台顯示「快速加入購物車」按鈕"""
    buy_now_button: Optional[Buy_Now_ButtonConfig] = None
    """Show the "Buy Now" Button in the Store or not.  全店是否顯示「立即購買按鈕」功能"""
    enabled_sort_by_sold: Optional[bool] = None
    """Show the "Sort by Product Sales Volume" filter in the Store or not.  前台是否顯示「商品銷量排序」篩選功能"""
    plp_wishlist: Optional[bool] = None
    """Show the "Add to Wishlist" Button on the Product List or not.  前台商品列表是否顯示「加入追蹤清單」按鈕"""
    opens_in_new_tab: Optional[bool] = None
    """Open a "new window" or use the "current window" when clicking on a product  點選商品時使用「新視窗開啟」還是「當前視窗」"""