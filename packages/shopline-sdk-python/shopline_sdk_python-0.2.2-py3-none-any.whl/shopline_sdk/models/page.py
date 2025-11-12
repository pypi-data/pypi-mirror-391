"""Shopline API 数据模型 - Page"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .link import Link
from .page_section_settings import PageSectionSettings
from .translatable import Translatable


class Page(BaseModel):
    id: Optional[str] = None
    """Id of the Page 頁面ID"""
    created_at: Optional[str] = None
    """Created Time 頁面創造時間"""
    updated_at: Optional[str] = None
    """Updated Time 頁面更新時間"""
    status: Optional[Union[Literal['active', 'draft', 'removed', 'hidden'], str]] = None
    """Status of the Page 頁面狀態"""
    type: Optional[str] = None
    """Type of the Page 頁面類別"""
    title_translations: Optional[Translatable] = None
    content_translations: Optional[Translatable] = None
    key: Optional[Union[Literal['about', 'terms', 'policy', 'others'], str]] = None
    """Key of the page"""
    seo_title_translations: Optional[Translatable] = None
    seo_description_translations: Optional[Translatable] = None
    seo_keywords: Optional[str] = None
    """Key of the page"""
    open_outside_window: Optional[bool] = None
    """Whether the page open outside window 頁面是否在視窗外開啟"""
    column_gutter: Optional[str] = None
    """The gutter of column 行的間距"""
    row_gutter: Optional[str] = None
    """The gutter of row 列的間距"""
    is_product_page: Optional[bool] = None
    """Whether the page is a product page 頁面是否商品頁面"""
    is_hidden_product_visible: Optional[bool] = None
    """Whether hidden product is visible in the page 頁面會否顯示已隱藏商品"""
    use_noindex_meta_tag: Optional[bool] = None
    """Whether the page is searchable on search engines 頁面會否被搜尋引擎搜尋到"""
    link: Optional[Link] = None
    sections: Optional[Dict[str, PageSectionSettings]] = None
    sections_order: Optional[List[str]] = None
    rows: Optional[List[Union[str, float, int, bool, List[Any], Dict[str, Any]]]] = None
    use_layout_engine_template: Optional[bool] = None
    """Whether the page has Layout Engine template 頁面是否使用 Layout Engine template"""