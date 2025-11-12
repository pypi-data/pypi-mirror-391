"""Shopline API 数据模型 - CustomerPromotion"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable



class Available_ChannelsItem(BaseModel):
    """Item model for available_channels"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: Optional[Translatable] = None

class CustomerPromotion(BaseModel):
    id: Optional[str] = None
    """Promotion ID 優惠活動ID"""
    title_translations: Optional[Translatable] = None
    discount_on: Optional[Union[Literal['order', 'item', 'category'], str]] = None
    """Promotion target 優惠套用對象 - order = Entire shop 全店 item = Specific item 指定商品 category = Specific category 指定分類"""
    first_purchase_only: Optional[bool] = None
    """For first purchase only 創建自動套用—每位會員限用優惠一次的任選優惠"""
    first_purchase_all_platform: Optional[bool] = None
    """For first purchase all platform 全通路首購"""
    codes: Optional[List[str]] = None
    """Coupon Code 促銷代碼"""
    user_max_use_count: Optional[int] = None
    """Limit per member 每會員最多使用次數 - null = Unlimited 不限使用次數"""
    max_use_count: Optional[int] = None
    """How many times can this promotion be used? 活動限使用次數 - null = Unlimited 不限使用次數"""
    use_count: Optional[int] = None
    """Usage of this layer of promotion 本階層活動已使用次數"""
    user_use_count: Optional[int] = None
    """用戶活動已使用次數"""
    start_at: Optional[str] = None
    """Promotion start time 活動開始時間"""
    end_at: Optional[str] = None
    """Promotion end time 活動結束時間 - null = no end date 永不過期"""
    available_platforms: Optional[List[str]] = None
    coupon_type: Optional[Union[Literal['draw', 'single', 'multi'], str]] = None
    drew_coupon_count: Optional[int] = None
    """How many times did this promotion been drew? 活動被領取次數"""
    discount_type: Optional[str] = None
    """discount type of the promotion  優惠券的折扣類型"""
    user_coupon_status: Optional[Union[Literal['active', 'used', 'inactive'], str]] = None
    """User Coupon Status, Only expose when coupon_type is draw  優惠卷領取狀態，只在領取型優惠卷顯示此欄位  active = 已領取  used = 已使用  inactive = 未領取"""
    available_channel_ids: Optional[List[str]] = None
    """Ids of available channel 指定通路ids"""
    available_channels: Optional[List[Available_ChannelsItem]] = None
    """available channel 指定通路"""
    condition_scope: Optional[str] = None
    """Promotion condition scope, Dependent on promotion's conditions, it could be 'discounted_subtotal', 'discounted_products', 'discounted_categories', or empty  優惠套用條件"""