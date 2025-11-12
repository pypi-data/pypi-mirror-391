"""Shopline API 数据模型 - CartItem"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .cart_product import CartProduct
from .cart_product_variation import CartProductVariation
from .cart_promotion import CartPromotion
from .money import Money
from .translatable import Translatable



class Item_DataConfig(BaseModel):
    """Configuration model for item_data"""
    name: Optional[str] = None
    ref_id: Optional[str] = None
    discount_type: Optional[str] = None
    selected_child_products: Optional[List[Dict[str, Any]]] = None

class CartItem(BaseModel):
    id: Optional[str] = None
    """Cart ID 購物車物品ID"""
    product_id: Optional[str] = None
    """Product ID 購物車內的商品ID"""
    variation_id: Optional[str] = None
    """Variation ID 購物車內的商品規格品ID"""
    quantity: Optional[float] = None
    """Quantity 購物車內的物品數量"""
    type: Optional[Union[Literal['product', 'product_set', 'subscription_product', 'manual_gift', 'custom_product', 'custom_discount', 'redeem_gift'], str]] = None
    """Type 購物車內的物品類型"""
    created_by: Optional[str] = None
    """The Source of Item  購物車物品加入的來源"""
    triggering_item_id: Optional[str] = None
    """Triggering Item ID 主商品的 ID（加購品才會有這個欄位）"""
    custom_price: Optional[Money] = None
    """Custom Price 自訂價格"""
    total_price: Optional[Money] = None
    """Total Price 自訂價格/商品總金額"""
    lock_info: Optional[Dict[str, Dict[str, Any]]] = None
    """Lock Inventory info 庫存鎖定資訊（直播場景）"""
    item_data: Optional[Item_DataConfig] = None
    """Information Of Item 購物車內的項目資訊"""
    product: Optional[CartProduct] = None
    """Product information Of the Item 購物車商品資訊"""
    variation: Optional[CartProductVariation] = None
    """Variation information Of the Item 購物車商品規格資訊"""
    applied_promotion: Optional[CartPromotion] = None
    """Applied Promotion information Of the Item 購物車商品套用優惠資訊"""