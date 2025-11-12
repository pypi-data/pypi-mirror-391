"""Shopline API 数据模型 - MemberPointRule"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .translatable import Translatable


class MemberPointRule(BaseModel):
    id: Optional[str] = None
    """Member Point Rule ID<br />會員點數ID"""
    status: Optional[Union[Literal['active', 'inactive'], str]] = None
    """Whether the rules is applying<br />規則是否正在生效"""
    unit_price: Optional[int] = None
    """The amount of purchase to earn a unit of points.<br /> This field will be null if the rule_type is not "earn_from_order."<br /> 賺取一個單位的點數所需的購買金額<br /> 如rule_type不是"earn_from_order"，此欄會是null"""
    points_per_unit: Optional[int] = None
    """The amount of points earned by a unit of unit_price.<br /> This field will be null if the rule_type is not "earn_from_order".<br /> 一個單位的unit_price能夠賺取的點數 如rule_type不是"earn_from_order"，此欄會是null"""
    points_expire_day: Optional[int] = None
    """The expiry date of points, null if there is no expiry date.<br /> This field will be null if the rule_type is not "earn_from_order".<br /> 點數的到期日，如規則並沒有設置點數會到期，此欄會是null 如rule_type不是"earn_from_order"，此欄會是null"""
    points_expire_month: Optional[int] = None
    """The expiry month of points, null if there is no expiry date.<br /> This field will be null if the rule_type is not "earn_from_order".<br /> 點數的到期月份，如規則並沒有設置點數會到期，此欄會是null 如rule_type不是"earn_from_order"，此欄會是null"""
    pending_days: Optional[int] = None
    """The number of days after delivery received (Arrived/ Collected) will the system automatically assign the point to customer.<br /> This field will be null if the rule_type is not "earn_from_order".＜br /> 顧客訂單轉變為 已取貨 / 已到達(宅配) 後幾天自動發送點數<br /> 如rule_type不是"earn_from_order"，此欄會是null"""
    rule_type: Optional[Union[Literal['earn_from_order', 'max_percentage_per_order', 'max_amount_per_order'], str]] = None
    """Define the types of rules that the current object is representing.<br /> 定義這個物件正在表示的規則類別"""
    remarks_translations: Optional[Translatable] = None
    membership_tier_id: Optional[str] = None
    """The id of membership_tier."""
    unit_point: Optional[int] = None
    """The amount of points needed to redeem a unit of discount.<br /> This field will be null if the rule_type is "earn_from_order".<br /> 兌換一個單位的折扣所需的點數<br /> 如rule_type是"earn_from_order"，此欄會是null"""
    price_per_unit: Optional[int] = None
    """The amount of discount per unit of points.<br /> This field will be null if the rule_type is "earn_from_order".<br /> 一個單位的點數兌換到的折扣<br /> 如rule_type是"earn_from_order"，此欄會是null"""
    point_value: Optional[int] = None
    """The price to apply point discount.<br /> It will be -1 if there is no constraint on applying discount.<br /> This field will be -1 if the rule_type is "earn_from_order".<br /> 可以使用折扣的價錢<br /> 如沒有設置使用折扣的價格，此欄會是-1<br /> 如rule_type是"earn_from_order"，此欄會是-1"""
    apply_threshold: Optional[int] = None
    """Maximum amount of point discount could be applied, the metric depends on the rule_type.<br /> This field will be null if the rule_type is "earn_from_order".<br /> 可使用的最高折扣額，此欄的單位會因應rule_type而改變<br /> 如rule_type是"earn_from_order"，此欄會是null"""
    available_platforms: Optional[List[str]] = None
    """Available platforms.<br />此規則生效的平台"""