"""Shopline API 数据模型 - Cart"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .cart_delivery import CartDelivery
from .cart_item import CartItem
from .coupon_item import CouponItem
from .money import Money
from .tax_info import TaxInfo
from .translatable import Translatable



class Applied_Tax_InfoConfig(BaseModel):
    """Configuration model for applied_tax_info"""
    sale: Optional[TaxInfo] = None
    """Sale Tax 基本消費稅"""
    Delivery: Optional[TaxInfo] = None
    """Delivery Fee Tax 運費稅"""


class Inclusive_Tax_InfoConfig(BaseModel):
    """Configuration model for inclusive_tax_info"""
    type: Optional[str] = None
    tax_region_id: Optional[str] = None
    rate: Optional[float] = None
    """Tax rate 套用稅率"""
    fee: Optional[Money] = None
    """Tax Fee 稅金"""
    country_code: Optional[str] = None
    """ISO Country Code 稅收國家或地區（ISO 標準國家代碼）"""
    tax_name: Optional[str] = None
    """Tax Name 稅金名稱"""


class Cart_TagsItem(BaseModel):
    """Item model for cart_tags"""
    id: Optional[str] = None
    """The Cart Tag ID 溫層 ID"""
    priority: Optional[float] = None
    """Priority 優先度"""
    name_translations: Optional[Translatable] = None
    """Name 名稱"""

class Cart(BaseModel):
    id: Optional[str] = None
    """Cart ID 購物車ID"""
    merchant_id: Optional[str] = None
    """Merchant ID 商家ID"""
    owner_id: Optional[str] = None
    """Owner ID 購物車擁有者ID，登入會員的購物車此值是 user_id; 訪客的購物車則是 public_session_id"""
    owner_type: Optional[Union[Literal['USER', 'GUEST'], str]] = None
    """Owner Type 購物車擁有者類型，登入會員的購物車此值是 User; 訪客的購物車則是 Guest"""
    page_id: Optional[str] = None
    """Page ID 一頁式商店 (express checkout)購物車的 page_id"""
    product_id: Optional[str] = None
    """Product ID 產品ID"""
    items: Optional[List[CartItem]] = None
    """Cart Items 購物車項目"""
    payment_id: Optional[str] = None
    """Payment ID 金流選項ID"""
    delivery_option_id: Optional[str] = None
    """Delivery Option ID 運送選項ID"""
    country: Optional[str] = None
    """Country 國家"""
    region_code: Optional[str] = None
    """Region Code 地區代碼"""
    postcode: Optional[str] = None
    """Postcode 郵遞區號"""
    referral_code: Optional[str] = None
    """Referral Code 推薦碼"""
    shop_session_id: Optional[str] = None
    """Shop Session ID 商店Session ID"""
    coupon_codes: Optional[List[str]] = None
    """Coupon Codes 優惠券代碼"""
    lock_inventory_ids: Optional[List[str]] = None
    """Lock Inventory IDs 鎖定庫存ID"""
    credit_apply_amount: Optional[float] = None
    """Credit Apply Amount 購物金折抵金額"""
    apply_member_point: Optional[float] = None
    """Apply Member Point 會員點數折抵數量"""
    delivery_data: Optional[Dict[str, Any]] = None
    """Delivery Data 運送資料"""
    delivery_address: Optional[Dict[str, Any]] = None
    """Delivery Address 運送地址"""
    payment_cod_type: Optional[Union[Literal['COD', 'NCOD'], str]] = None
    """Payment COD Type 貨到付款類型，COD是貨到付款; NCOD是非貨到付款"""
    total: Optional[Money] = None
    """Total 購物車合計"""
    subtotal: Optional[Money] = None
    """Subtotal 購物車小計"""
    applied_credits_limit: Optional[Money] = None
    """Applied User Credits Limit 折抵購物金上限"""
    applied_user_credits: Optional[Money] = None
    """Applied User Credits 折抵購物金"""
    total_tax_fee: Optional[Money] = None
    """Total Tax Fee 稅費合計"""
    delivery_fee: Optional[Money] = None
    """Delivery Fee 運費"""
    payment_fee: Optional[Money] = None
    """Payment Fee 附加費"""
    user_credit_balance: Optional[float] = None
    """User Credit Balance 購物金餘額"""
    applied_tax_info: Optional[Applied_Tax_InfoConfig] = None
    """Applied Tax Info 已套用稅金資訊"""
    inclusive_tax_info: Optional[Inclusive_Tax_InfoConfig] = None
    """Inclusive Tax Info 商品內含稅金"""
    custom_discount_items: Optional[List[CartItem]] = None
    """Custom Discount Items 自訂折扣項目(**deprecated**)"""
    coupons: Optional[List[CouponItem]] = None
    """Coupons Items 套用優惠項目"""
    affiliate_data: Optional[Dict[str, Dict[str, Any]]] = None
    """Cart Affiliate Data 購物車附屬屬性（社交電商場景）"""
    sale_event_info: Optional[Dict[str, Dict[str, Any]]] = None
    """Sale Event Information 直播場景資訊（社交電商場景）"""
    deliveries: Optional[List[CartDelivery]] = None
    """The Delivery Options Contained In The Cart 購物車包含之送貨方式（多購物車場景）"""
    cart_tags: Optional[List[Cart_TagsItem]] = None
    """The Cart Tags Contained In The Cart 購物車包含之溫層（多購物車場景）"""
    multi_cart_data: Optional[Dict[str, Dict[str, Any]]] = None
    """Calculating Data Of Each Cart Tag 每個溫層之計算資料（多購物車場景）"""
    created_at: Optional[str] = None
    """Created At 建立時間"""
    updated_at: Optional[str] = None
    """Updated At 更新時間"""