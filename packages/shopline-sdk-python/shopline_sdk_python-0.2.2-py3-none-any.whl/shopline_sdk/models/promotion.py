"""Shopline API 数据模型 - Promotion"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .extend_promotion import ExtendPromotion
from .link import Link
from .media import Media
from .money import Money
from .promotion_condition import PromotionCondition
from .translatable import Translatable


class Promotion(BaseModel):
    id: Optional[str] = None
    """Promotion ID 優惠活動ID"""
    discount_percentage: Optional[float] = None
    """Discount percentage 折扣百分比 - *Applicable when discount_type is percentage 當discount_type為percentage時適用"""
    discount_amount: Optional[Money] = None
    discountable_quantity: Optional[int] = None
    """Quantity 獲得數量 - *When discount_type is gift, this field refers to quantity of gift 當discount_type為gift時，此為贈品數量  *When discount_type is addon, this field refers to quality of add-on 當discount_type為addon時，此為可加購數量"""
    discounted_point: Optional[int] = None
    """Amount of point to redeem gift 點數兌換 - *Applicable when discount_type is member_point_redeem_gift 當discount_type為member_point_redeem_gift時適用"""
    discounted_price: Optional[Money] = None
    discountable_product_ids: Optional[List[str]] = None
    """Ids of Discounted product 指定商品ids"""
    conditions: Optional[List[PromotionCondition]] = None
    created_at: Optional[str] = None
    """Created Time 建立時間"""
    updated_at: Optional[str] = None
    """Updated Time 更新時間"""
    title_translations: Optional[Translatable] = None
    discountable_category_ids: Optional[List[str]] = None
    """Ids of Discounted category 指定商品分類ids"""
    discount_on: Optional[Union[Literal['order', 'item', 'category'], str]] = None
    """Promotion target 優惠套用對象 - order = Entire shop 全店 item = Specific item 指定商品 category = Specific category 指定分類"""
    discount_type: Optional[Union[Literal['percentage', 'amount', 'gift', 'addon', 'free_shipping', 'bundle_pricing', 'bundle_group', 'member_point_redeem_gift', 'subscription_gift'], str]] = None
    """Discount type 折扣類型 - percentage: 折扣% amount: 固定金額 gift: 贈品 addon: 加購品 free_shipping: 免運 bundle_pricing: 任選優惠 bundle_group: A+B組合優惠（紅配綠） member_point_redeem_gift: 點數兌換贈品 subscription_gift"""
    is_accumulated: Optional[bool] = None
    """Is bundle pricing or bundle pricing accumulated? 任選優惠/A+B組合優惠是否累計"""
    first_purchase_only: Optional[bool] = None
    """For first purchase only 創建自動套用—每位會員限用優惠一次的任選優惠"""
    first_purchase_all_platform: Optional[bool] = None
    """For first purchase all platform 全通路首購"""
    codes: Optional[List[str]] = None
    """Coupon Code 促銷代碼"""
    show_coupon: Optional[bool] = None
    membership_tier_id: Optional[str] = None
    requires_membership: Optional[bool] = None
    """Does it require membership? 設定目標群組 - false: 所有顧客 true: 會員"""
    whitelisted_membership_tier_ids: Optional[List[str]] = None
    """Specific Membership Tiers 適用會員等級"""
    whitelisted_tag_contents: Optional[List[str]] = None
    user_max_use_count: Optional[int] = None
    """Limit per member 每會員最多使用次數 - null = Unlimited 不限使用次數"""
    max_use_count: Optional[int] = None
    """How many times can this promotion be used? 活動限使用次數 - null = Unlimited 不限使用次數"""
    use_count: Optional[int] = None
    """Usage of this layer of promotion 本階層活動已使用次數"""
    sum_use_count: Optional[int] = None
    """Total usage of promotion 活動已使用次數"""
    whitelisted_delivery_option_ids: Optional[List[str]] = None
    """Delivery options that applicable to the promotion 活動適用送貨方式"""
    whitelisted_payment_ids: Optional[List[str]] = None
    """Payment options that applicable to the promotion 活動適用付款方式"""
    start_at: Optional[str] = None
    """Promotion start time 活動開始時間"""
    end_at: Optional[str] = None
    """Promotion end time 活動結束時間 - null = no end date 永不過期"""
    status: Optional[Union[Literal['active', 'draft', 'hidden'], str]] = None
    """Promotion status 活動狀態 - active: 上架 draft: 下架 hidden: 會員默認優惠/主商品加購品 removed: 刪除"""
    usable: Optional[bool] = None
    """Is promotion active 優惠是否進行中 - true: published and not expired上架且沒有過期 false: unpublished or published and expired上架已過期 或是 下架"""
    for_affiliate_campaign: Optional[bool] = None
    """Is applicable to affiliate campaign 是否適用於推薦活動"""
    is_contain_campaign: Optional[bool] = None
    """Is binded to affiliate campaign 是否已綁定推薦活動"""
    seo_enabled: Optional[bool] = None
    """Generate promotion page and SEO sitemap or not"""
    seo_keywords: Optional[str] = None
    """SEO keywords SEO 關鍵字"""
    seo_description_translations: Optional[Translatable] = None
    seo_title_translations: Optional[Translatable] = None
    link: Optional[Link] = None
    available_platforms: Optional[List[str]] = None
    """指定平台（目前僅接受 "ec", "retail", "app" 值）"""
    is_partial_free_shipping: Optional[bool] = None
    coupon_type: Optional[Union[Literal['draw', 'single', 'multi'], str]] = None
    extended_promotion_id: Optional[str] = None
    """Parent promotion id 母層活動id - *applicable when this is a child promotion"""
    extend_promotions: Optional[List[ExtendPromotion]] = None
    """多階層優惠活動與條件"""
    drew_coupon_count: Optional[int] = None
    """How many times did this promotion been drew? 活動被領取次數"""
    whitelisted_membership_tiers: Optional[List[Dict[str, Any]]] = None
    """指定會員資料"""
    summary: Optional[Dict[str, Any]] = None
    """優惠概況"""
    available_channel_ids: Optional[List[str]] = None
    """Ids of available channel 指定通路ids"""
    banner_medias: Optional[Media] = None
    term_translations: Optional[Translatable] = None