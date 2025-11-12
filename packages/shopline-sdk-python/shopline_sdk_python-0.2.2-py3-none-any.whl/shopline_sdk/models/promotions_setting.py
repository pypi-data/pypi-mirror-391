"""Shopline API 数据模型 - PromotionsSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class PromotionsSetting(BaseModel):
    one_coupon_limit_enabled: Optional[bool] = None
    """Checkout Limitation to One Coupon  購物車限用一組優惠代碼"""
    show_promotion_reminder: Optional[bool] = None
    """Show non-applied 'Free Shipping' promotion reminder on checkout page  顯示未套用 '免運費' 活動提示於結帳購物車"""
    show_coupon: Optional[bool] = None
    """Show 'Coupon' in Storefront Member Center  網店會員中心顯示 '優惠券'"""
    multi_order_discount_strategy: Optional[Union[Literal['order_or_tier_promotion', 'order_and_tier_promotions', 'multi_order_and_tier_promotions'], str]] = None
    """Order-Level Discount Setting  全店折扣優惠套用設定  order_or_tier_promotion:    Apply the promotion with largest discount among order-level discount promotions and membership offer.    結帳擇優套用一組 全店滿額滿件折扣優惠 或 會員等級默認優惠  order_and_tier_promotions    Apply the promotion with largest discount among order-level discount promotions first and apply membership offer afterward.    結帳擇優套用一組 全店滿額滿件折扣優惠後，疊加套用會員等級默認優惠  multi_order_and_tier_promotions    Apply multiple order-level discount promotions first and and apply membership offer afterward.   結帳疊加套用多組 全店滿額滿件折扣優惠 與 會員等級默認優惠"""
    order_promotions_ignore_exclude_product: Optional[bool] = None
    """Order-level discount / Membership offer exclude 'product not applicable to discount'  全店折扣優惠/會員等級默認優惠 排除「不適用折扣商品」"""
    order_gift_exclude_credit_and_point: Optional[bool] = None
    """[DEPRECATED] Total order over Minimum Amount Gift promotion condition deduct Credits and Points.  全店滿額送贈品優惠條件扣除 折抵購物金 與 點數折現  This field will be deprecated. Please use `order_gift_threshold_mode` instead.  此欄位即將淘汰，請改用 `order_gift_threshold_mode`。"""
    order_gift_threshold_mode: Optional[Union[Literal['after_price_discounts', 'after_all_discounts'], str]] = None
    """Gift Promotion – Minimum Amount Settings  全店滿額送贈品  - `after_price_discounts`: Minimum amount is calculated as: Cart subtotal - Discounts (default)    滿額條件以（購物車小計 - 折扣）計算（默認選中）  - `after_all_discounts`: Minimum amount is calculated as: Cart subtotal - Discounts - Credits - Points    滿額條件以（購物車小計 - 折扣 - 折抵購物金 - 點數折現）計算"""
    category_item_gift_threshold_mode: Optional[Union[Literal['before_discounts', 'after_price_discounts', 'after_all_discounts'], str]] = None
    """Free gift for selected products/categories over a minimum amount  指定商品／分類滿額送贈品  - `before_discounts`: Minimum amount is calculated as: Selected product subtotal (default)    滿額條件以（指定商品小計）計算（默認選中）  - `after_price_discounts`: Minimum amount is calculated as: Selected product subtotal - Discounts    滿額條件以（指定商品小計 - 折扣）計算  - `after_all_discounts`: Minimum amount is calculated as: Selected product subtotal - Discounts - Credits - Points    滿額條件以（指定商品小計 - 折扣 - 折抵購物金 - 點數折現）計算"""
    order_free_shipping_threshold_mode: Optional[Union[Literal['after_price_discounts', 'after_all_discounts'], str]] = None
    """Free shipping for order over a minimum amount  全店滿額免運費  - `after_price_discounts`: Minimum amount is calculated as: Cart subtotal - Discounts    滿額條件以（購物車小計 - 折扣）計算  - `after_all_discounts`: Minimum amount is calculated as: Cart subtotal - Discounts - Credits - Points (default)    滿額條件以（購物車小計 - 折扣 - 折抵購物金 - 點數折現）計算（默認選中）"""
    category_item_free_shipping_threshold_mode: Optional[Union[Literal['before_discounts', 'after_price_discounts', 'after_all_discounts'], str]] = None
    """Free shipping for selected products/categories over a minimum amount  指定商品／分類滿額免運費  - `before_discounts`: Minimum amount is calculated as: Selected product subtotal (default)    滿額條件以（指定商品小計）計算（默認選中）  - `after_price_discounts`: Minimum amount is calculated as: Selected product subtotal - Discounts    滿額條件以（指定商品小計 - 折扣）計算  - `after_all_discounts`: Minimum amount is calculated as: Selected product subtotal - Discounts - Credits - Points    滿額條件以（指定商品小計 - 折扣 - 折抵購物金 - 點數折現）計算"""