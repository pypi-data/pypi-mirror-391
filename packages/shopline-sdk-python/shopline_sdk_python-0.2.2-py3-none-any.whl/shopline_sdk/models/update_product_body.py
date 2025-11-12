"""Shopline API 数据模型 - UpdateProductBody"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .product import Product
from .product_variation import ProductVariation
from .translatable import Translatable



class Variant_Custom_Type_TranslationsItem(BaseModel):
    """Item model for variant_custom_type_translations"""
    name_translations: Optional[Translatable] = None
    type: Optional[str] = None

class UpdateProductBody(BaseModel):
    """Payload for updating product"""
    title_translations: Optional[Translatable] = None
    summary_translations: Optional[Translatable] = None
    description_translations: Optional[Translatable] = None
    show_custom_related_products: Optional[bool] = None
    related_product_ids: Optional[List[str]] = None
    same_price: Optional[bool] = None
    location_id: Optional[str] = None
    sku: Optional[str] = None
    seo_title_translations: Optional[Translatable] = None
    seo_description_translations: Optional[Translatable] = None
    seo_keywords: Optional[str] = None
    link: Optional[str] = None
    is_reminder_active: Optional[bool] = None
    is_preorder: Optional[bool] = None
    preorder_limit: Optional[int] = None
    preorder_note_translations: Optional[Translatable] = None
    max_order_quantity: Optional[int] = None
    weight: Optional[float] = None
    tags: Optional[str] = None
    """Tags 標籤  *Tags are used to search products at the admin panel and help  set up the product-related coupons.  標籤功能用作商品搜尋，並能為指定商品設置優惠券的用途。"""
    blacklisted_delivery_option_ids: Optional[List[str]] = None
    blacklisted_payment_ids: Optional[List[str]] = None
    available_start_time: Optional[str] = None
    available_end_time: Optional[str] = None
    schedule_publish_at: Optional[str] = None
    category_ids: Optional[List[str]] = None
    tax_type: Optional[str] = None
    """Tax type 國內稅項"""
    oversea_tax_type: Optional[str] = None
    """Oversea tax type 海外稅項"""
    status: Optional[Union[Literal['active', 'draft', 'removed', 'hidden'], str]] = None
    images: Optional[List[str]] = None
    detail_images: Optional[List[str]] = None
    """Additional Product Photos 更多商品圖片"""
    gtin: Optional[str] = None
    barcode_type: Optional[Union[Literal['Code 128', 'Bookland EAN', 'ISBN'], str]] = None
    variant_custom_type_translations: Optional[List[Variant_Custom_Type_TranslationsItem]] = None
    variant_options: Optional[List[Dict[str, Any]]] = None
    is_replace_variations: Optional[bool] = None
    """Is replacing variations? 是否更換全部規格?"""
    variations: Optional[List[ProductVariation]] = None
    unlimited_quantity: Optional[bool] = None
    default_show_image_selector: Optional[bool] = None
    """Show variation photos. 展示商品規格圖像。"""
    allow_gift: Optional[bool] = None
    """Specifies whether the item can be set as a gift.  是否可以設為贈品  true: the product can be set as a gift.  false: the product cannot be set as a gift."""