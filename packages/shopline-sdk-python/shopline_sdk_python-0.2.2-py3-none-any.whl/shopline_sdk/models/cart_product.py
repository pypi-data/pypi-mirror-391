"""Shopline API 数据模型 - CartProduct"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .translatable import Translatable



class Field_TitlesItem(BaseModel):
    """Item model for field_titles"""
    key: Optional[str] = None
    label: Optional[str] = None
    name_translations: Optional[Translatable] = None


class Flash_Price_SetsItem(BaseModel):
    """Item model for flash_price_sets"""
    start_at: Optional[str] = None
    end_at: Optional[str] = None

class CartProduct(BaseModel):
    id: Optional[str] = None
    """Product ID 商品 ID"""
    title_translations: Optional[Translatable] = None
    """Product Name 商品名稱"""
    type: Optional[str] = None
    """Product Type 商品類型"""
    same_price: Optional[bool] = None
    """Main Product and Variation Product share the same price (Including original price and member price)  規格商品是否皆同主商品價格，包含原價格與會員價"""
    price: Optional[Money] = None
    """Price 商品原價格"""
    is_preorder: Optional[bool] = None
    """Pre-ordered or not 是否開放預購"""
    sku: Optional[str] = None
    """Stock Keeping Unit 商品貨號"""
    blacklisted_payment_ids: Optional[List[str]] = None
    """Excluded Payment Method 排除的付款方式"""
    blacklisted_delivery_option_ids: Optional[List[str]] = None
    """Excluded Delivery Options 排除的送貨方式"""
    out_of_stock_orderable: Optional[float] = None
    """Product's Current total orderable quantity 商品目前可購買總數量 -  *If unlimited_quantity is true or out_of_stock_orderable is true  this field will return -1"""
    is_excluded_promotion: Optional[bool] = None
    """product is exclude promotion which is discount on order 不適用全店折扣的優惠是否開啟"""
    field_titles: Optional[List[Field_TitlesItem]] = None
    """Field Title Data 規格名稱"""
    max_order_quantity: Optional[float] = None
    """set maximum quantity per purchase for this product  商品單次購買上限  *-1 represents there's no quantity limit for each purchase  -1代表無商品單次購買的上限"""
    created_by: Optional[str] = None
    """The Channel Product established through 商品建立管道"""
    subscription_enabled: Optional[bool] = None
    """subscription_enabled 是否為定期購商品"""
    flash_price_sets: Optional[List[Flash_Price_SetsItem]] = None
    """Price for Flash Campaign 限時促銷價"""
    cart_tag_id: Optional[str] = None
    """The Cart Tag Configured For The Product 商品設定的溫層屬性"""
    unlimited_quantity: Optional[bool] = None
    """Unlimited product quantity or not 商品數量是否無限"""
    lowest_member_price: Optional[Money] = None
    """Lowest Member Price 會員最低價格"""
    quantity: Optional[float] = None
    """Quantity 商品數量"""
    cover_media: Optional[Dict[str, Any]] = None
    """Product Cover 商品封面"""
    child_products: Optional[List[Dict[str, Any]]] = None
    """Product Set Contained Child Products 組合商品之子商品"""
    member_price: Optional[Money] = None
    """Member Price 會員價"""
    price_sale: Optional[Money] = None
    """Price on sale 特價"""
    total_orderable_quantity: Optional[float] = None
    """Product's Current total orderable quantity 商品目前可購買總數量 -  *If unlimited_quantity is true or out_of_stock_orderable is true  this field will return -1"""
    preorder_limit: Optional[float] = None
    """Pre-ordere Limit 預購上限"""
    has_variation: Optional[bool] = None
    """Has Variation 是否為多規格商品"""
    updated_at: Optional[str] = None
    """Last Updated Time 商品最後更新時間"""
    created_at: Optional[str] = None
    """Product Created Time 商品創建時間"""