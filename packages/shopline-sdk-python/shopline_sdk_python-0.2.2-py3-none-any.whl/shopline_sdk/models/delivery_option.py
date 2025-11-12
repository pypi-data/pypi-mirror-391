"""Shopline API 数据模型 - DeliveryOption"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .translatable import Translatable



class Config_DataConfig(BaseModel):
    """Configuration model for config_data"""
    support_cod: Optional[bool] = None
    """Support Cash on Delivery (COD) 支持代收貨款 (COD)"""
    lead_time: Optional[int] = None
    """Lead Time (no more than 30 days) 預估備貨天數（最多30天）"""
    max_lead_time: Optional[int] = None
    """Selectable day length (from lead time)  備貨期後可指定的天數長度"""
    excluded_weekdays: Optional[List[int]] = None
    """Sunday=0; Monday=1"""
    excluded_dates: Optional[List[str]] = None
    delivery_time_required: Optional[bool] = None
    """Specified Timeslot (Enabled: Customers can set up estimated delivery arrival time in case no receiver at home.)  出貨訂單需指定時段 (啟用功能：可以設定商品到貨的時間，避免無人收貨的情況。)"""
    specific_delivery_time_translations: Optional[Translatable] = None
    delivery_target_area: Optional[Union[Literal['localOnly', 'outlyingIslandOnly', 'all'], str]] = None
    """For Taiwan only. You can set whether Main area or Outlying Island delivery service  台灣地區可進階設定本島/外島的配送區域    localOnly: Main Area delivery service 提供本島配送  outlyingIslandOnly: Outlying Island delivery service 提供外島配送  all: all of the above 以上皆是"""


class Delivery_RatesItem(BaseModel):
    """Item model for delivery_rates"""
    countries: Optional[List[str]] = None
    """Shipping Countries/ Regions 配送國家／地區    * means rest of the world 所有未被選取的國家／地區"""
    rate_limit: Optional[Any] = None
    """weight(kg). -1 for infinity. Please supply -1 if delivery_type = flat.  重量(kg)。-1 代表無限。如 fee_type 為 flat ，請輸入 -1。"""
    fee: Optional[Money] = None

class DeliveryOption(BaseModel):
    id: Optional[str] = None
    """Delivery Option ID 送貨方式ID"""
    status: Optional[Union[Literal['active', 'draft'], str]] = None
    """Delivery Option Status 送貨方式狀態 - Status allows: active 啟用中 draft 隱藏"""
    name_translations: Optional[Translatable] = None
    requires_customer_address: Optional[bool] = None
    """Requires Customer Address 需要顧客提供地址"""
    show_description_on_checkout: Optional[bool] = None
    """Display description on the checkout page 在結帳頁面上顯示送貨方式簡介"""
    description_translations: Optional[Translatable] = None
    delivery_time_description_translations: Optional[Translatable] = None
    fee_type: Optional[Union[Literal['flat', 'flat_weight', 'subtotal', 'item_count', 'sl_logistic'], str]] = None
    """Fee Type 收費模式 - Fee type allow: flat  flat_weight  subtotal  item_count * sl_logistic"""
    form_fields: Optional[List[Dict[str, Any]]] = None
    region_type: Optional[str] = None
    """Delivery Option Code 送貨方式代碼  store_pickup: 門市自取  custom: 自訂  sfexpress: 順豐速運  tw_711_nopay: 7-11 取貨不付款 (C2C)  tw_711_pay: 7-11 取貨付款 (C2C)  tw_711_b2c_nopay: 7-11 取貨不付款 (B2C)  tw_711_b2c_pay: 7-11 取貨付款 (B2C)  emap_only_711: 7-11 超商取貨 (純地圖)  tw_simple_711: 7-11 取貨 (無串接)  cross_border_711_store_pick_up: 7-11 跨境門市取貨不付款  cross_border_711_home_delivery: 7-11 跨境宅配  tw_simple_familymart: 全家取貨 (無串接)  tw_ezship: ezship 超商取貨付款  711_return_nopay: 7-11 退貨便 (C2B)  tw_fm_b2c_nopay: 全家 取貨不付款 (B2C)  tw_fm_b2c_pay: 全家 取貨付款 (B2C)  tw_fm_c2c_nopay: 全家 取貨不付款 (C2C)  tw_fm_c2c_pay: 全家 取貨付款 (C2C)  emap_only_fm: 全家超商取貨 (純地圖)  hk_sfplus: Zeek斑馬快送  hk_integrated_sfexpress: 順豐速運 (串接)  hk_integrated_sf_pickup: 順豐速運 (串接)  hk_pakpobox: Alfred 智能櫃  tw_tcat_roomtemp: 黑貓宅配 - 常溫  tw_tcat_roomtemp_cod: 黑貓宅配 - 常溫 (貨到付款)  tw_tcat_refrigerated: 黑貓宅配 - 冷藏  tw_tcat_refrigerated_cod: 黑貓宅配 - 冷藏 (貨到付款)  tw_tcat_frozen: 黑貓宅配 - 冷凍  tw_tcat_frozen_cod: 黑貓宅配 - 冷凍 (貨到付款)  custom_return: 自訂退貨  ninja_van: Ninja Van - 需取件  sl_logistics_fmt_freeze_pay: 全家 冷凍取貨付款 (B2C)  sl_logistics_fmt_freeze_nopay: 全家 冷凍取貨不付款 (B2C)  sl_logistics_ninjavan: Ninja Van (經由 SL logistics)  sl_logistics_ninjavan_cod: Ninja Van 貨到付款 (經由 SL logistics)  sl_logistics_kerry_th_nd: Kerry ND（經由 SL logistics）  sl_logistics_kerry_th_nd_cod: Kerry ND 貨到付款（經由 SL logistics）  sl_logistics_kerry_th_2d: Kerry 宅配（標準）  sl_logistics_kerry_th_2d_cod: Kerry 宅配 - 貨到付款（標準）  sl_logistics_kerry_th_3d: Kerry 3D（經由 SL logistics）  sl_logistics_kerry_th_3d_cod: Kerry 3D 貨到付款（經由 SL logistics）  sl_logistics_yto_home: 中國 - 台灣物流專線宅配（標準 - 普貨）  sl_logistics_yto_home_cod: 中國 - 台灣物流專線宅配- 貨到付款（標準 - 普貨）  sl_logistics_yto_store: 中國 - 台灣物流專線超取 - 取貨不付款（標準 - 普貨）  sl_logistics_yto_store_cod: 中國 - 台灣物流專線超取 - 取貨付款（標準 - 普貨）  sl_logistics_yto_special_home: 中國 - 台灣物流專線宅配（標準 - 特貨）  sl_logistics_yto_special_home_cod: 中國 - 台灣物流專線宅配- 貨到付款（標準 - 特貨）  sl_logistics_yto_special_store: 中國 - 台灣物流專線超取 - 取貨不付款（標準 - 特貨）  sl_logistics_yto_special_store_cod: 中國 - 台灣物流專線超取 - 取貨付款（標準 - 特貨）"""
    delivery_type: Optional[str] = None
    excluded_payment_ids: Optional[List[str]] = None
    """Excluded Payment Method IDs 該送貨方式排除的付款方式ID"""
    config_data: Optional[Config_DataConfig] = None
    """Configuration Data 物流設置資訊"""
    supported_countries: Optional[List[str]] = None
    """Supported Countries 可支援配送區域"""
    delivery_rates: Optional[List[Delivery_RatesItem]] = None
    """Delivery Fee 運費"""
    approved: Optional[bool] = None
    """true 設定且已審核 false 未設定或未審核通過"""
    support_cod: Optional[bool] = None
    """Support COD payment  支援 COD 付款  allows: true 設定且已審核 false 未設定或未審核通過"""
    support_non_cod: Optional[bool] = None
    """Support non COD payment  支援 非 COD 付款  allows: true 設定且已審核 false 未設定或未審核通過"""
    store_pickup_option: Optional[Dict[str, Any]] = None
    """For delivery option type as store_pickup, it shows the information of the stores.  物流類別為門市自取的送貨方式可用，顯示門市資訊。"""
    is_return: Optional[bool] = None
    """Is It Return Delivery 是否為退貨"""