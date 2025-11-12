"""Shopline API 数据模型 - Theme"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class Theme(BaseModel):
    id: Optional[str] = None
    """Id of the Theme 主題ID"""
    created_at: Optional[str] = None
    """Created Time 主題創造時間"""
    updated_at: Optional[str] = None
    """Updated Time 主題更新時間"""
    caption: Optional[str] = None
    """Caption of the theme 主題的說明文字"""
    demo_url: Optional[str] = None
    """Demo URL of the theme 主題的示範網址"""
    description: Optional[str] = None
    """Description of the theme 主題的抽述"""
    highlight_url: Optional[str] = None
    """Highlight URL of the theme 主題的網址"""
    key: Optional[str] = None
    """Key of the theme 主題的鍵"""
    media_ids: Optional[List[str]] = None
    """The id of the medias that belongs to this theme 主題包含的媒體ID"""
    name: Optional[str] = None
    """Name of the Theme 主題的名稱"""
    path: Optional[str] = None
    """Path of the Theme 主題的路徑"""
    rollout_keys: Optional[List[str]] = None
    """Rollout Keys of the Theme 主題的 Rollout Keys"""
    status: Optional[Union[Literal['active', 'draft', 'removed', 'hidden'], str]] = None
    """Status of the Theme 主題狀態"""
    type: Optional[str] = None
    """Type of the Theme 主題類別"""
    support_new_page_builder: Optional[bool] = None
    """Support new page section type 這個theme是否支援section page格式"""
    new_page_builder_rollout_key: Optional[str] = None
    """The merchant should have this rollout key in order to create or edit pages of this theme in NPB  店家需有這條 rollout key 才能在NPB創建／編輯這個主題的頁面"""
    support_new_plp: Optional[bool] = None
    """Support Product List Page 這個theme是否支援product list page"""
    new_plp_rollout_key: Optional[str] = None
    """Rollout key of Product List Page  Product List Page 的 Rollout Key (用於判斷前台是否支援 PLP)"""