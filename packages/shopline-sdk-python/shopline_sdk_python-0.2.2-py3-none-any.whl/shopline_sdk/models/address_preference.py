"""Shopline API 数据模型 - AddressPreference"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .address_preference_layout_data import AddressPreferenceLayoutData
from .translatable import Translatable



class LayoutConfig(BaseModel):
    """Configuration model for layout"""
    large: Optional[AddressPreferenceLayoutData] = None
    medium: Optional[AddressPreferenceLayoutData] = None
    small: Optional[AddressPreferenceLayoutData] = None

class AddressPreference(BaseModel):
    """The definition of address format.For more information, please refer <a href=https://shopline.atlassian.net/wiki/spaces/EN/pages/3136521533/Address+module+->here</a> 地址格式定義，詳細請參考<a href=https://shopline.atlassian.net/wiki/spaces/EN/pages/3136521533/Address+module+->文件</a>"""
    id: Optional[str] = None
    """Address preference ID 地址格式ID"""
    country_code: Optional[Union[Literal['TW', 'US', 'VN', 'JP', 'MY', 'PH', 'SG', 'TH', 'CA', 'DE', 'FR', 'GB', 'HK', 'ID', 'DEFAULT'], str]] = None
    """Country code 國碼"""
    priority: Optional[int] = None
    """The order in which address information is filled in 地址資料填寫的順序"""
    level: Optional[int] = None
    """The level of address nodes. 地址節點的等級"""
    field_name: Optional[Union[Literal['address_1', 'address_2', 'city', 'country', 'district', 'postcode', 'state'], str]] = None
    """Field name 欄位名稱"""
    display: Optional[bool] = None
    """Display or not 是否需要顯示"""
    required: Optional[bool] = None
    """Address preference is required or not 欄位是否為必填"""
    type: Optional[Union[Literal['dropdown', 'input'], str]] = None
    """Input type for UI 資料填寫表單介面顯示該欄位的模式"""
    layout: Optional[LayoutConfig] = None
    """The definition of address display in different size of device 在各種裝置大小下的地址顯示定義"""
    rule: Optional[str] = None
    """The regular expression rule of postcode 用以驗證郵遞區號的正規表達式規則"""
    placeholder_translations: Optional[Translatable] = None
    """Display before input 輸入前的顯示文字"""
    title_translations: Optional[Translatable] = None
    """Title Translations 地址格式名稱"""
    address_separator: Optional[str] = None
    """Punctuation to stick address values together 將地址各欄位值結合在一起的分隔符"""