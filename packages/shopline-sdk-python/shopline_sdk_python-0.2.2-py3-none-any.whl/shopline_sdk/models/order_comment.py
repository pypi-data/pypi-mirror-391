"""Shopline API 数据模型 - OrderComment"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .media import Media


class OrderComment(BaseModel):
    id: Optional[str] = None
    """ID of the comment 訂單通訊的id"""
    created_at: Optional[str] = None
    """Created Time 創建時間"""
    updated_at: Optional[str] = None
    """Updated Time 更新時間"""
    text: Optional[str] = None
    """The message of the comment 該訂單通訊的訊息內容"""
    owner_id: Optional[str] = None
    """The owner id of the comment 該訂單通訊發出者的id"""
    owner_type: Optional[str] = None
    """The owner id of the comment 該訂單通訊發出者的類型"""
    trackable_id: Optional[str] = None
    trackable_type: Optional[str] = None
    is_private: Optional[bool] = None
    """The type of the comment. If true, the message can only be viewed by the shop admin.  If false, the message can also be viewed by the customer.  訂單通訊的類型。若為true，則該訂單通訊只能被網店管理查看。  若為false，則顧客也可查看。"""
    media: Optional[Media] = None