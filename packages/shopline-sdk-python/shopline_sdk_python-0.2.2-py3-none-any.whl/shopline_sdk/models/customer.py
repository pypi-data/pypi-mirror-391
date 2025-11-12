"""Shopline API 数据模型 - Customer"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .channel import Channel
from .custom_field import CustomField
from .membership_tier_rule import MembershipTierRule
from .money import Money
from .order_delivery_address import OrderDeliveryAddress
from .translatable import Translatable
from .utm_data import UtmData



class Membership_TierConfig(BaseModel):
    """Configuration model for membership_tier"""
    id: Optional[str] = None
    """Membership tier's ID 會員等級ID"""
    level: Optional[int] = None
    """Level of Current Membership Tier 等級高低"""
    name_translations: Optional[Translatable] = None
    status: Optional[str] = None
    """Membership tier's status 會員等級狀態"""


class Membership_Tier_GapConfig(BaseModel):
    """Configuration model for membership_tier_gap"""
    next_tier: Optional[Dict[str, Any]] = None
    """Membership Tier Data 顧客會員等級"""
    next_discount: Optional[float] = None
    """The discount of next membership tier<br />下一個會員等級的折扣優惠"""
    user_spending: Optional[float] = None
    """The amount used to determine if a member meets the upgrade criteria, based on the "Membership Upgrade Condition" in the SHOPLINE Admin:  - For "Single Purchase," returns the highest order amount that meets the threshold   during the membership period, or 0 if none meet the threshold.  - For "Purchase within specified period," returns the total spending within that period.  Returns null if the member is already at the highest tier.    用於判斷會員是否符合升級條件的消費金額，依據 Admin 中的「會員升級條件」設定決定回傳值：  - 若條件為「單次購物」，檢查目前會籍期間內是否有任一筆訂單達到門檻。若有訂單達門檻，則回傳金額最高者；若皆未達門檻，回傳 0。  - 若條件為「指定期限內購物」，回傳在指定期限內的累積消費金額。  若會員已達最高等級，則回傳 null。"""
    user_spendings_for_extend: Optional[float] = None
    """The amount used to determine if a member meets the extend criteria, based on the "Membership extension condition" in the SHOPLINE Admin:  - For "Single Purchase," returns the highest order amount that meets the threshold   during the membership period, or 0 if none meet the threshold.  - For "Purchase within specified period," returns the total spending within that period.  Returns null if the current membership has a permanent duration.    用於判斷會員是否符合續會條件的消費金額，依據 Admin 中的「會員續會條件」設定決定回傳值：  - 若條件為「單次購物」，檢查目前會籍期間內是否有任一筆訂單達到門檻。若有訂單達門檻，則回傳金額最高者；若皆未達門檻，回傳 0。  - 若條件為「指定期限內購物」，回傳在指定期限內的累積消費金額。  若當前會籍為永久期限，則回傳 null。"""
    next_total_spending: Optional[float] = None
    """The amount of upgrading to next membership tier.<br /> 升等到下一會員等級所需之消費金額（Admin 設定的升級金額條件）  *若沒有下一級則回傳 null"""
    extend_total_spending: Optional[float] = None
    """The amount of extending in current membership tier.<br /> 續會目前會員等級所需之消費金額（Admin 設定的續會金額條件）  *若沒有設定則回傳 null"""


class Current_Membership_Tier_InfoConfig(BaseModel):
    """Configuration model for current_membership_tier_info"""
    id: Optional[str] = Field(default=None, alias="_id")
    """Membership tier's ID 會員等級ID"""
    level: Optional[int] = None
    """Level of Current Membership Tier 等級高低"""
    name_translations: Optional[Translatable] = None
    merchant_id: Optional[str] = None
    """merchant ID"""
    exclusive_product_count: Optional[int] = None
    """Number of exlcusive products in this membership tier  這個會員級別不能購買的產品數目"""
    promotion_count: Optional[int] = None
    """Number of promotions in this membership tier  這個會員級別的優惠數目"""
    valid_period: Optional[Dict[str, Any]] = None
    """Valid period of this membership tier  這個會員級別的有效時段"""
    membership_tier_rules: Optional[List[MembershipTierRule]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SubscriptionsItem(BaseModel):
    """Item model for subscriptions"""
    is_active: Optional[bool] = None
    platform: Optional[str] = None


class Orders_TotalsItem(BaseModel):
    """Item model for orders_totals"""
    id: Optional[str] = None
    """Order ID 訂單ID"""
    total: Optional[Money] = None
    platform: Optional[str] = None
    """The platform that creates the order 創建此訂單的平台"""


class Member_Info_RewardConfig(BaseModel):
    """Configuration model for member_info_reward"""
    custom_fields: Optional[List[Any]] = None
    """Custom fields that qualify for data rewards will be recognized.  會認列資料獎賞的自定義欄位"""
    reward_on: Optional[List[Any]] = None
    """The fields that qualify for data rewards will be recognized.  會認列資料獎賞的基本欄位"""
    promotion_ids: Optional[List[Any]] = None
    """The promotion IDs of the rewards.  獎賞的 promotion IDs   If the merchant did not choose to offer a promotion reward, it will be null.  如果店家沒有選擇提供優惠獎賞，則為 null"""
    user_credits: Optional[int] = None
    """The user credits of the rewards.  獎賞的購物金   If the merchant did not choose to offer a shopping credit reward, it will be null.  如果店家沒有選擇提供購物金獎賞，則為 null"""
    member_points: Optional[int] = None
    """The member points of the rewards.  獎賞的會員點數   If the merchant did not choose to offer a member point reward, it will be null.  如果店家沒有選擇提供會員點數獎賞，則為 null"""

class Customer(BaseModel):
    id: Optional[str] = None
    """Customer Unique ID 顧客ID"""
    name: Optional[str] = None
    """Customer Name 顧客姓名"""
    email: Optional[str] = None
    """Customer Email 顧客電子郵件"""
    gender: Optional[Union[Literal['male', 'female', 'other'], str]] = None
    """Customer Gender 顧客性別"""
    birthday: Optional[str] = None
    """Customer Birthday 顧客生日  Please use birth_year, birth_month, birth_day instead.  The field is compatible with the old version.  請使用 birth_year, birth_month, birth_day 代替  此欄位為舊版相容用   If birth_year is null, then the default year is 1904.  如果 birth_year 為 null, 則預設為 1904 年   If birth_month is null, then the default month is 1.  如果 birth_month 為 null, 則預設為 1 月   If birth_day is null, then the default day is 1.  如果 birth_day 為 null, 則預設為 1 日"""
    birth_year: Optional[int] = None
    """Customer Birth Year 顧客出生年份"""
    birth_month: Optional[int] = None
    """Customer Birth Month 顧客出生月份"""
    birth_day: Optional[int] = None
    """Customer Birth Day 顧客出生日期"""
    memo: Optional[str] = None
    """Customer memo 顧客備註"""
    phones: Optional[List[str]] = None
    """Customer Phones 顧客電話 - *If customer mobile phone is confirmed, this field is hidden. 如果顧客手機已經確認,此欄位則會被隱藏"""
    phone: Optional[str] = None
    """Customer Phone 顧客電話 - *If customer mobile phone is confirmed, this field is hidden. 如果顧客手機已經確認,此欄位則會被隱藏  This should be the last item in `phones` field.  此電話為 `phones` 欄位的最後一項"""
    phone_country_code: Optional[str] = None
    """Customer Phone Country Code 顧客電話國碼"""
    mobile_phone: Optional[str] = None
    """Customer Mobile Phone 顧客手機 - *If customer mobile phone is confirmed, this field is displayed. 如果顧客手機已經確認,此欄位則會被顯示"""
    mobile_phone_verified: Optional[bool] = None
    """Mobile Phone is Verified or not 是否手機驗證"""
    mobile_phone_country_calling_code: Optional[str] = None
    """Country Code of Mobile Phone 手機號碼國碼"""
    locale_code: Optional[str] = None
    """Customer Locale Code 顧客使用前台之語言"""
    order_count: Optional[int] = None
    """Customer Order Number 顧客累積訂單數"""
    orders_total_sum: Optional[Money] = None
    is_member: Optional[bool] = None
    """Is the customer a member? 顧客是否為會員？"""
    is_blacklisted: Optional[bool] = None
    """Is the customer in black-list? 顧客是否在黑名單？"""
    is_subscribed_marketing_email: Optional[bool] = None
    """Does the customer subscribe marketing email? 顧客是否接受優惠宣傳？"""
    credit_balance: Optional[int] = None
    """Current Customer Credits 顧客購物金餘額"""
    member_point_balance: Optional[int] = None
    """Current Member Points 顧客會員點數餘額"""
    custom_data: Optional[List[CustomField]] = None
    membership_tier: Optional[Membership_TierConfig] = None
    """Membership Tier Data 顧客會員等級"""
    delivery_addresses: Optional[List[OrderDeliveryAddress]] = None
    """Customer's Delivery Addresses 顧客送貨地址"""
    subscribed_email_types: Optional[List[str]] = None
    """Subscribed Email Types 訂閱消息類型"""
    ref_user_id: Optional[str] = None
    """For third party to put custom user_id 可供儲存第三方顧客ID"""
    line_id: Optional[str] = None
    """LINE ID 顧客Line ID"""
    facebook_id: Optional[str] = None
    """FACEBOOK ID 顧客FACEBOOK ID"""
    google_id: Optional[str] = None
    """GOOGLE ID 顧客GOOGLE ID"""
    updated_at: Optional[str] = None
    """Customer Last Updated Time 顧客最後更新資訊時間 - *UTC Time"""
    created_at: Optional[str] = None
    """Customer Created Time 顧客資料創造時間 - *UTC Time"""
    current_sign_in_at: Optional[str] = None
    """Timestamp updated when customers sign in 顧客最後登入時間"""
    last_sign_in_at: Optional[str] = None
    """Holds the timestamp of the previous sign in 顧客上一次登入時間"""
    registered_at: Optional[str] = None
    """Customer register's Date and time 顧客註冊時間"""
    registered_from_channel: Optional[Channel] = None
    created_by: Optional[Union[Literal['shop', 'admin', 'openapi', 'shop_crm', 'pos'], str]] = None
    """顧客建立來源 "shop" 來自前台網站  "admin" 來自後台 "openapi" 由open api創建  "shop_crm" 來自 kiosk "pos"來自 POS"""
    created_by_channel: Optional[str] = None
    """顧客建立店家來源"""
    tags: Optional[List[str]] = None
    """自定義標籤"""
    tier_expires_at: Optional[str] = None
    """Membership expiry date 會籍到期日"""
    confirmed_at: Optional[str] = None
    """timestamp of the email verification 顧客確認電郵注册時間"""
    utm_data: Optional[UtmData] = None
    referral_code: Optional[str] = None
    """Referral code 推薦碼"""
    offline_referral_registered_at: Optional[str] = None
    """Referral Registered At 門市綁定時間"""
    offline_referral_channel_id: Optional[str] = None
    """Referral Channel ID 門市 ID"""
    offline_referral_agent_id: Optional[str] = None
    """Referral Agent ID 門市推薦人 ID"""
    membership_tier_gap: Optional[Membership_Tier_GapConfig] = None
    """Next membership tier's info 下一個會員等級的資料"""
    current_membership_tier_info: Optional[Current_Membership_Tier_InfoConfig] = None
    """Current membership tier's info 現時的會員等級的資料"""
    metafields: Optional[Dict[str, Any]] = None
    """metafields only show if include_fields[]=metafields"""
    customer_authentication_linkings: Optional[List[str]] = None
    """3rd Party Customer Authentication（SSO）  SSO 第三方串接相關資訊   * 備註：串接 SSO 的會員 ID 不會存在 ref_user_id，會存在 customer_authentication_linkings 中的 ref_id"""
    subscriptions: Optional[List[SubscriptionsItem]] = None
    """Subscriptions  *SMS subscription is an async operation  , so the field might not show the result immediately"""
    orders_totals: Optional[List[Orders_TotalsItem]] = None
    member_info_reward: Optional[Member_Info_RewardConfig] = None
    """Member Info Reward  會員資料獎賞   If a customer has not yet filled out the relevant fields of information but qualifies for a data reward, the reward content and fields will be returned.  如果顧客尚未填寫相關欄位的資料，且顧客符合資料獎賞的資格則會返回獎賞內容及欄位。   only show if include_fields[]=member_info_reward of GET customer API  只有在 GET customer API 中 include_fields[]=member_info_reward 時才會顯示"""
    info_reward_triggered: Optional[bool] = None
    """If the Update Customer API is called to update customer information and triggers the sending of a customer data reward, it will be true.  如果呼叫 Update Customer API 更新顧客資料並觸發發送顧客資料獎賞，則為 true"""
    info_reward_claimed: Optional[bool] = None
    """Whether the customer has claimed the info reward 顧客是否已經領取資料獎賞"""