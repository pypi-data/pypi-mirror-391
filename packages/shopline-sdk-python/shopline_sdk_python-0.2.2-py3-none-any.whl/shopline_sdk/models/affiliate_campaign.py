"""Shopline API 数据模型 - AffiliateCampaign"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .campaign_product import CampaignProduct
from .money import Money
from .translatable import Translatable


class AffiliateCampaign(BaseModel):
    id: Optional[str] = None
    """Affiliate Campaign Unique ID 推薦活動ID"""
    name: Optional[str] = None
    """Affiliate Campaign Name 推薦活動名稱"""
    condition_value: Optional[int] = None
    """Condition for total order over how much money to get the reward 全單超過多少錢可以獲得回饋"""
    reward_type: Optional[Union[Literal[None, 'amount', 'percentage'], str]] = None
    """Reward type 訂單回饋類型"""
    reward_value: Optional[int] = None
    """Reward value 訂單回饋值"""
    promotion_id: Optional[str] = None
    """Promotion id 套用優惠折扣 ID"""
    code: Optional[str] = None
    """Affiliate code 推薦代碼"""
    referral_link: Optional[str] = None
    """Referral link 推薦連結"""
    partner_info: Optional[Dict[str, Any]] = None
    """Partner Info 合作夥伴資訊"""
    apply_on: Optional[Union[Literal['order', 'product'], str]] = None
    """Apply on order or product 套用於訂單或商品"""
    apply_method: Optional[Union[Literal['all', 'product'], str]] = None
    """Apply method  套用方式:  - all: 全部  - item: 逐筆設定"""
    use_count: Optional[int] = None
    """Use count 使用次數"""
    affiliate_percentage: Optional[float] = None
    """Affiliate percentage 分潤百分比"""
    affiliate_amount: Optional[Money] = None
    condition_min_amount: Optional[Money] = None
    campaign_products: Optional[CampaignProduct] = None
    start_at: Optional[str] = None
    """Affiliate campaign start time 推薦活動開始時間 - *UTC Time"""
    end_at: Optional[str] = None
    """Affiliate campaign end time 推薦活動結束時間 - *UTC Time"""
    remarks_translations: Optional[Translatable] = None
    created_at: Optional[str] = None
    """Affiliate campaign created time 推薦活動創建時間 - *UTC Time"""
    updated_at: Optional[str] = None
    """Affiliate campaign updated time 推薦活動更新時間 - *UTC Time"""
    total_reward_value: Optional[Money] = None
    """total reward value of orders"""