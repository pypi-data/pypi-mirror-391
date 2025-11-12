"""Shopline API 数据模型 - ProductReviewSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Review_Reward_ConditionConfig(BaseModel):
    """Configuration model for review_reward_condition"""
    min_length: Optional[int] = None
    """Minimum comment length required 最少評論字數"""
    deadline_days: Optional[int] = None
    """Deadline days for reward 評價在order完成後送出的期限天數"""
    picture_upload: Optional[int] = None
    """Picture upload required 圖片上傳要求"""

class ProductReviewSetting(BaseModel):
    hide_review: Optional[bool] = None
    """Hide Review 是否隱藏評價"""
    hide: Optional[List[Union[Literal['1', '2', '3', '4', '5'], str]]] = None
    """Hide Reviews of Given Stars 隱藏評價星等"""
    show_media: Optional[bool] = None
    """Show Media 是否顯示圖片"""
    allow_customer_upload_media: Optional[bool] = None
    """Allow Upload Media 評價是否可以上傳圖片"""
    enable_reward: Optional[bool] = None
    """Enable Reward 是否開啟評價獎賞"""
    reward_type: Optional[Union[Literal['user_credit', 'member_point'], str]] = None
    """Reward Type 評價獎賞類別"""
    review_reward_condition: Optional[Review_Reward_ConditionConfig] = None
    """Reward Condition 評價獎賞條件"""