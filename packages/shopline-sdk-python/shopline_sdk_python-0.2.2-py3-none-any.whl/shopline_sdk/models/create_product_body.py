"""Shopline API 数据模型 - CreateProductBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .product import Product
from .product_variation import ProductVariation
from .translatable import Translatable



class ProductConfig(BaseModel):
    """Configuration model for product"""
    price: Optional[float] = None
    """Product Price 原價格"""
    price_sale: Optional[float] = None
    """Product Sale Price 特價"""
    retail_price: Optional[float] = None
    """Retail Price 零售價"""
    member_price: Optional[float] = None
    """Member Price 會員價"""
    cost: Optional[float] = None
    """Product Cost 成本價"""
    product_price_tiers: Optional[Dict[str, str]] = None
    """Membership tier's ID 會員等級ID"""
    hide_price: Optional[bool] = None
    same_price: Optional[bool] = None
    quantity: Optional[float] = None
    """Quantity 商品數量 -  If the product contains variations with quantity, this field will be the sum of quantities of all variations.  Otherwise, the product quantity is between 0 to 9999999.  如果商品有不同規格及數量，商品數量將會是所有規格商品數量的總和。  否則，商品數量要在 0 - 9999999 之間。"""
    unlimited_quantity: Optional[bool] = None
    location_id: Optional[str] = None
    sku: Optional[str] = None
    category_ids: Optional[List[str]] = None
    title_translations: Optional[Translatable] = None
    summary_translations: Optional[Translatable] = None
    description_translations: Optional[Translatable] = None
    seo_title_translations: Optional[Translatable] = None
    seo_description_translations: Optional[Translatable] = None
    seo_keywords: Optional[str] = None
    link: Optional[str] = None
    is_preorder: Optional[bool] = None
    preorder_limit: Optional[int] = None
    preorder_note_translations: Optional[Translatable] = None
    is_reminder_active: Optional[bool] = None
    show_custom_related_products: Optional[bool] = None
    related_product_ids: Optional[List[str]] = None
    weight: Optional[float] = None
    tags: Optional[str] = None
    """Tags 標籤  *Tags are used to search products at the admin panel and help set up  the product-related coupons.  標籤功能用作商品搜尋，並能為指定商品設置優惠券的用途。"""
    blacklisted_delivery_option_ids: Optional[List[str]] = None
    blacklisted_payment_ids: Optional[List[str]] = None
    max_order_quantity: Optional[int] = None
    created_by: Optional[Union[Literal['catcher', 'pos', 'sc'], str]] = None
    supplier_id: Optional[str] = None
    available_start_time: Optional[str] = None
    available_end_time: Optional[str] = None
    schedule_publish_at: Optional[str] = None
    tax_type: Optional[str] = None
    """Tax type 國內稅項"""
    oversea_tax_type: Optional[str] = None
    """Oversea tax type 海外稅項"""
    status: Optional[Union[Literal['active', 'draft', 'removed', 'hidden'], str]] = None
    images: Optional[List[str]] = None
    """Product Main Photos. If the images field is null, the system will upload a default image.  商品主圖片，如images為空，將會帶入系統預設圖片"""
    detail_images: Optional[List[str]] = None
    """Additional Product Photos 更多商品圖片"""
    variant_options: Optional[List[Dict[str, Any]]] = None
    variant_custom_type_translations: Optional[List[Dict[str, Any]]] = None
    variations: Optional[List[ProductVariation]] = None
    all_variations: Optional[bool] = None
    """Set if all combinations of variation options should be used or not.  設定是否需要使用所有商品規格選項的組合。   when "same_price" is set as "false", "all_variations" is not applicable.  當"same_price"被設定為false，"all_variations"不適用。"""
    channel_id: Optional[str] = None
    allow_gift: Optional[bool] = None
    """Specifies whether the item can be set as a gift.  是否可以設為贈品  true: the product can be set as a gift.  false: the product cannot be set as a gift."""

class CreateProductBody(BaseModel):
    """Payload for creating product"""
    ignore_product_media_errors: Optional[bool] = None
    """Do not raise error when failed to upload media 上傳圖像失敗時不報錯"""
    default_show_image_selector: Optional[bool] = None
    """Show product variations image on product page 在產品頁面上顯示產品規格圖像"""
    product: Optional[ProductConfig] = None