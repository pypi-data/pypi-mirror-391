"""Shopline API 数据模型 - Product"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .category import Category
from .filter_tag import FilterTag
from .media import Media
from .money import Money
from .product_price_tier import ProductPriceTier
from .product_variation import ProductVariation
from .translatable import Translatable



class Flash_Price_SetsItem(BaseModel):
    """Item model for flash_price_sets"""
    id: Optional[str] = None
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    price_set: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class Field_TitlesItem(BaseModel):
    """Item model for field_titles"""
    key: Optional[str] = None
    label: Optional[str] = None
    name_translations: Optional[Translatable] = None


class Variant_OptionsItem(BaseModel):
    """Item model for variant_options"""
    id: Optional[str] = None
    name_translations: Optional[Translatable] = None
    type: Optional[Union[Literal['color', 'size', 'custom_1', 'custom_2', 'custom_3'], str]] = None
    media: Optional[Dict[str, Any]] = None
    index: Optional[int] = None


class Feed_CategoryConfig(BaseModel):
    """Configuration model for feed_category"""
    google_category_id: Optional[str] = None
    google_option_id: Optional[str] = None
    google_product_category: Optional[str] = None


class Bundle_SetConfig(BaseModel):
    """Configuration model for bundle_set"""
    id: Optional[str] = Field(default=None, alias="_id")
    price_type: Optional[Union[Literal['fixed_amount discount_percentage discount_amount'], str]] = None
    """Price Type 組合售價類型"""
    discount_value: Optional[float] = None
    """Discount Value 金額折扣  When price_type is 'fixed_amount', example: 20 means price_sale $20  If discount_value is null, its value is taken from the price_sale  當組合售價類型是固定組合價時，20代表组合售價为 $20. 如果該值為空, 金額折扣值取自特價  When price_type is 'discount_percentage', example: 20 for 80% off; 70 for 30% off  當組合售價類型是折扣比例時，20代表八折; 70代表三折  When price_type is 'discount_amount', example: 20 means minus $20; 70 means minus $70  當組合售價類型是金額折扣時，20代表減$20; 70代表減$70"""
    bundle_set_products: Optional[Dict[str, Any]] = None

class Product(BaseModel):
    id: Optional[str] = None
    """Product's ID 商品ID"""
    status: Optional[Union[Literal['active', 'draft', 'removed', 'hidden'], str]] = None
    """Product's status 商品狀態 - true: Published 上架  false: Unpublished 下架 "active": Published 上架 "draft": Unpublished 下架  "hidden": hidden 隱藏  Default: false"""
    retail_status: Optional[Union[Literal['active', 'draft'], str]] = None
    """POS product's status POS商品狀態 -  "active": Published 上架  "draft": Unpublished 下架   Default: active"""
    title_translations: Optional[Translatable] = None
    summary_translations: Optional[Translatable] = None
    price: Optional[Money] = None
    price_sale: Optional[Money] = None
    lowest_price: Optional[Money] = None
    lowest_price_sale: Optional[Money] = None
    hide_price: Optional[bool] = None
    """Hide Price to customers 隱藏價格 - *Default: false"""
    same_price: Optional[bool] = None
    """Main Product and Variation Product share the same price (Including original price and member price)  規格商品是否皆同主商品價格，包含原價格與會員價  1. If same price is true, main product price is required and will be apply to all variation prices  2. If same price is false, variation price is required and each variation can apply different prices."""
    cost: Optional[Money] = None
    member_price: Optional[Money] = None
    retail_price: Optional[Money] = None
    flash_price_sets: Optional[List[Flash_Price_SetsItem]] = None
    """price for flash campaign 限時促銷價"""
    is_preorder: Optional[bool] = None
    """Pre-ordered or not 是否開放預購"""
    preorder_limit: Optional[int] = None
    """Pre-ordere Limit 預購上限"""
    preorder_note_translations: Optional[Translatable] = None
    """Pre-order Note Info 預購資訊"""
    weight: Optional[float] = None
    """Product's Weight (kg) 商品重量 (公斤)"""
    quantity: Optional[float] = None
    """Product's Current quantity 商品目前數量 -  *If unlimited_quantity is true, the product has unlimited quantity  regardless of the quantity showing here"""
    total_orderable_quantity: Optional[float] = None
    """Product's Current total orderable quantity 商品目前可購買總數量 -  *If unlimited_quantity is true or out_of_stock_orderable is true  this field will return -1"""
    unlimited_quantity: Optional[bool] = None
    """Unlimited product quantity or not. 商品數量是否無限"""
    medias: Optional[List[Media]] = None
    """Media Data 媒體(照片)資訊"""
    detail_medias: Optional[List[Media]] = None
    """Additional Product Photos 更多商品圖片 Maximum 20 images for a product. 最多 20 張圖片"""
    category_ids: Optional[List[str]] = None
    """Categories' IDs 商品所屬分類之ID"""
    supplier: Optional[str] = None
    """Supplier 供應商"""
    sku: Optional[str] = None
    """Stock Keeping Unit 商品貨號"""
    barcode: Optional[str] = None
    """Product's Barcode 商品條碼編號"""
    quantity_sold: Optional[int] = None
    """Product's Quantity Sold 商品銷售數量"""
    barcode_type: Optional[Union[Literal['Code 128', 'Bookland EAN', 'ISBN'], str]] = None
    """Barcode type 商品條碼編號類別"""
    field_titles: Optional[List[Field_TitlesItem]] = None
    """Field Title Data 規格名稱"""
    variations: Optional[List[ProductVariation]] = None
    """Product Variations Data 商品規格資訊"""
    variant_options: Optional[List[Variant_OptionsItem]] = None
    """Product Variations 商品規格 -  Maximum 3 types of variant option for a product, type allow (color, size, custom_1, custom_2, custom_3)  最多支援三種不同的 type, type 支援(color, size, custom_1, custom_2, custom_3)"""
    categories: Optional[List[Category]] = None
    """Categories Data 商品分類資訊"""
    location_id: Optional[str] = None
    """Stock Unit Number 儲位編號"""
    feed_category: Optional[Feed_CategoryConfig] = None
    """Category for different feed 廣告的分類"""
    description_translations: Optional[Translatable] = None
    """Product Description 商品描述"""
    seo_title_translations: Optional[Translatable] = None
    """Title of SEO SEO優化標題"""
    seo_description_translations: Optional[Translatable] = None
    """Description of SEO SEO優化描述"""
    seo_keywords: Optional[str] = None
    """Keywords of SEO SEO關鍵字  *Keywords should be separated by commas (,) max length 160 characters.  關鍵字以逗號(,)分隔, 最長 160字"""
    link: Optional[str] = None
    is_reminder_active: Optional[bool] = None
    """Out-Of-Stock Reminder 商品缺貨是否提醒"""
    show_custom_related_products: Optional[bool] = None
    """Show Custom Related products 顯示相關商品"""
    related_product_ids: Optional[List[str]] = None
    """Custom related products 自訂相關商品"""
    tags: Optional[List[str]] = None
    """Tags 標籤  *Tags are used to search products at the admin panel and help set up the product-related coupons.  標籤功能用作商品搜尋，並能為指定商品設置優惠券的用途。"""
    blacklisted_delivery_option_ids: Optional[List[str]] = None
    """Excluded Delivery Options 排除的送貨方式"""
    blacklisted_payment_ids: Optional[List[str]] = None
    """Excluded Payment Options 排除的付款方式"""
    max_order_quantity: Optional[int] = None
    """set maximum quantity per purchase for this product  商品單次購買上限  *-1 represents there's no quantity limit for each purchase  -1代表無商品單次購買的上限"""
    gender: Optional[str] = None
    """Mapping Product Category: Gender 產品使用類別：性別  male 男性  female 女性 * unisex 男女通用"""
    age_group: Optional[str] = None
    """Mapping Product Category:Age Group 產品使用類別：年齡層  newborn 新生兒  infant 嬰兒  toddler 幼兒  kids兒童 * Adult 成人"""
    adult: Optional[str] = None
    """Mapping Product Category:Adult 產品使用類別：成人  yes 是  no 否"""
    condition: Optional[str] = None
    """Mapping Product Category:Condition 產品使用類別：狀況  used 二手  refurbished 整新品 * new 新品"""
    brand: Optional[str] = None
    """Brand 商品品牌"""
    mpn: Optional[str] = None
    """Manufacturer Part Number 製造編號"""
    gtin: Optional[str] = None
    """Barcode 商品條碼編號"""
    blacklisted_feed_channels: Optional[List[str]] = None
    """排除這個商品投放管道 Exclude this product to channel"""
    updated_at: Optional[str] = None
    """Last Updated Time 商品最後更新時間"""
    created_at: Optional[str] = None
    """Product Created Time 商品創建時間"""
    available_start_time: Optional[str] = None
    available_end_time: Optional[str] = None
    created_by: Optional[str] = None
    is_excluded_promotion: Optional[bool] = None
    """product is exclude promotion which is discount on order 不適用全店折扣的優惠是否開啟"""
    taxable: Optional[bool] = None
    """taxable 是否收稅"""
    labels: Optional[List[Translatable]] = None
    """product labels 標簽的商品促銷標簽文案"""
    locked_inventory_count: Optional[float] = None
    schedule_publish_at: Optional[str] = None
    product_price_tiers: Optional[List[ProductPriceTier]] = None
    """Product's price for member tier.   適用於指定會員分級的產品價格。"""
    metafields: Optional[Dict[str, Any]] = None
    """metafields only show if include_fields[]=metafields"""
    out_of_stock_orderable: Optional[bool] = None
    """out_of_stock_orderable 缺貨時是否可接單"""
    subscription_enabled: Optional[bool] = None
    """subscription_enabled 是否為定期購商品。"""
    subscription_period_duration: Optional[int] = None
    """subscription_period_duration 定期購天數"""
    subscription_recurring_count_limit: Optional[int] = None
    """Subscription recurring count limit 定期購期數"""
    filter_tags: Optional[List[FilterTag]] = None
    """filter_tags 自訂篩選條件"""
    bundle_set: Optional[Bundle_SetConfig] = None
    """bundle_set info 組合商品資訊  Only provided when include_fields contains 'bundle_set'  僅於include_fields傳入 'bundle_set' 時提供"""
    type: Optional[str] = None
    """product type 商品型別  Only provided when include_fields contains 'type'  僅於include_fields傳入 'type' 時提供"""
    tax_type: Optional[str] = None
    """Tax type 國內稅項"""
    oversea_tax_type: Optional[str] = None
    """Oversea tax type 海外稅項"""
    allow_gift: Optional[bool] = None
    """Specifies whether the item can be set as a gift.  是否可以設為贈品  true: the product can be set as a gift.  false: the product cannot be set as a gift."""