"""Shopline API 数据模型 - OrderItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .media import Media
from .money import Money
from .product import Product
from .translatable import Translatable
from .translatable_array import TranslatableArray



class Item_DataConfig(BaseModel):
    """Configuration model for item_data"""
    variation_data: Optional[Dict[str, Any]] = None
    """Variation data of the item (if applicable), including price, weight and more  商品規格的數據(如適用)，包括價格、重量等"""
    affiliate_data: Optional[Dict[str, Any]] = None
    """Affiliate data of the item (if applicable), including affiliate_percentage or affiliate_amount  商品分潤的資料(如適用)，包括分潤百分比或分潤金額"""


class Object_DataConfig(BaseModel):
    """Configuration model for object_data"""
    gender: Optional[str] = None
    age_group: Optional[str] = None
    adult: Optional[str] = None
    condition: Optional[str] = None
    brand: Optional[str] = None
    supplier: Optional[Any] = None
    """Supplier  供應商  -  Only provided when include_fields contains 'supplier'  僅於include_fields傳入 'supplier' 時提供"""
    weight: Optional[float] = None
    barcode_type: Optional[Union[Literal['Code 128', 'Bookland EAN', 'ISBN'], str]] = None
    location_id: Optional[str] = None
    max_order_quantity: Optional[int] = None
    gtin: Optional[str] = None
    mpn: Optional[str] = None


class Child_ProductsConfig(BaseModel):
    """Configuration model for child_products"""
    id: Optional[str] = None
    """ID of Product/Addon Product/Gift 商品/加購品/贈品的ID  (Custom Product doesn't have a item_id) (自訂商品沒有item_id)"""
    title_translations: Optional[Translatable] = None
    fields_translations: Optional[TranslatableArray] = None
    variation_id: Optional[str] = None
    """The variation ID 規格商品ID"""
    sku: Optional[str] = None
    """Product SKU 商品貨號"""
    price: Optional[Money] = None
    price_sale: Optional[Money] = None

class OrderItem(BaseModel):
    id: Optional[str] = None
    """Order item's ID (ID of an order item's collection, including item_type, item_id..and so on)  系統自行創建訂單品項ID"""
    item_type: Optional[Union[Literal['Product', 'AddonProduct', 'Gift', 'CustomProduct'], str]] = None
    """Order item type: Product  商品  AddonProduct 加購品 Gift 贈品 CustomProduct 自訂商品"""
    item_data: Optional[Item_DataConfig] = None
    """CartItem snapshot 在第三方合作夥伴下單之前,在購物車內時的資訊快照"""
    item_id: Optional[str] = None
    """ID of Product/Addon Product/Gift 商品/加購品/贈品的ID  (Custom Product doesn't have a item_id) (自訂商品沒有item_id)"""
    item_variation_id: Optional[str] = None
    """(To-Be-Deprecated) 規格商品ID請使用下方item_variation_key欄位"""
    item_variation_key: Optional[str] = None
    """Variation ID 規格商品的ID"""
    item_price: Optional[Money] = None
    price: Optional[Money] = None
    price_sale: Optional[Money] = None
    cost: Optional[Money] = None
    item_points: Optional[int] = None
    """Points used for single item 兌換商品所需點數"""
    title_translations: Optional[Translatable] = None
    fields_translations: Optional[TranslatableArray] = None
    sku: Optional[str] = None
    """Product SKU 商品貨號"""
    is_preorder: Optional[bool] = None
    """Is preorder 是否是預購商品"""
    preorder_note_translations: Optional[Translatable] = None
    quantity: Optional[int] = None
    """Order item quantity 商品數量"""
    total: Optional[Money] = None
    order_discounted_price: Optional[Money] = None
    discounted_price: Optional[Money] = None
    total_points: Optional[int] = None
    """Total points cost on same product (item_points * quantity)  此商品的總點數"""
    media: Optional[Media] = None
    product_subscription_id: Optional[str] = None
    """ID of Product Subscription 定期購的ID"""
    object_data: Optional[Object_DataConfig] = None
    """Object data  商品數據"""
    child_products: Optional[Child_ProductsConfig] = None
    """The products in a product set 組合商品內的商品  Appear only when item_type is productSet 只有item_type是組合商品才會出現"""