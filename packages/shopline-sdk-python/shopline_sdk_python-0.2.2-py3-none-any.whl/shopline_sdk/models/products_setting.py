"""Shopline API 数据模型 - ProductsSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class ProductsSetting(BaseModel):
    enabled_pos_product_customized_price: Optional[bool] = None
    enabled_pos_product_price_tier: Optional[bool] = None
    enabled_product_review: Optional[bool] = None
    """Enable product review. 啟用商品評價"""
    price_range_enabled: Optional[bool] = None
    """Show Price Range in the Store 前台顯示「價格區間」"""
    variation_display: Optional[Union[Literal['dropdown', 'swatches'], str]] = None
    """Display style for product variations in the store (Dropdown selection or Label swatches).  商品規格於商店的顯示方式為「下拉選單」或「文字選項」"""
    addon_limit_enabled: Optional[bool] = None
    """Addon Limit Enabled 加購品數量上限"""
    enabled_show_member_price: Optional[bool] = None
    """Show member price in the store. 在前台顯示「會員價」"""
    enabled_stock_reminder: Optional[bool] = None
    """Show Low Inventory Reminder in the Store 在前台顯示「低庫存」提示"""
    show_sold_out: Optional[bool] = None
    """Show Sold Out Reminder in the Store 前台顯示「售完」提示"""
    enabled_pos_pinned_product: Optional[bool] = None
    """Enable pos pinned product. 啟用 POS 釘選商品功能"""
    show_max_discount_rate: Optional[Dict[str, Any]] = None
    """Show max discount rate in the store. 在前台顯示「最低折扣規格」，與折扣的顯示方式"""