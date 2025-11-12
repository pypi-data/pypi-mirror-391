"""Shopline API 数据模型 - Order"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money
from .order_agent import OrderAgent
from .order_campaign_item import OrderCampaignItem
from .order_customer_info import OrderCustomerInfo
from .order_delivery import OrderDelivery
from .order_delivery_address import OrderDeliveryAddress
from .order_delivery_data import OrderDeliveryData
from .order_invoice import OrderInvoice
from .order_item import OrderItem
from .order_payment import OrderPayment
from .order_promotion_item import OrderPromotionItem
from .order_source import OrderSource
from .utm_data import UtmData



class InvoicesItem(BaseModel):
    """Item model for invoices"""
    tax_id: Optional[str] = None
    mailing_address: Optional[str] = None
    invoice_type: Optional[Union[Literal['0', '1', '2'], str]] = None
    buyer_name: Optional[str] = None
    carrier_type: Optional[Union[Literal['0', '1', '2'], str]] = None
    carrier_number: Optional[str] = None
    n_p_o_b_a_n: Optional[str] = None
    invoice_tax_type: Optional[Union[Literal['1', '2', '5'], str]] = None
    invoice_number: Optional[str] = None
    invoice_status: Optional[Union[Literal['active', 'cancel'], str]] = None
    invoice_date: Optional[str] = None


class Order_CommentsItem(BaseModel):
    """Item model for order_comments"""
    owner_type: Optional[Union[Literal['Merchant', 'User'], str]] = None
    value: Optional[str] = None
    time: Optional[str] = None


class Order_NotesItem(BaseModel):
    """Item model for order_notes"""
    owner_type: Optional[Union[Literal['Merchant', 'User'], str]] = None
    value: Optional[str] = None
    time: Optional[str] = None


class ChannelConfig(BaseModel):
    """Configuration model for channel"""
    created_by_channel_id: Optional[str] = None
    created_by_channel_name: Optional[Dict[str, Any]] = None


class Applied_Tax_InfoConfig(BaseModel):
    """Configuration model for applied_tax_info"""
    sales: Optional[Dict[str, Any]] = None
    delivery: Optional[Dict[str, Any]] = None


class Auto_Reward_Credit_SummaryConfig(BaseModel):
    """Configuration model for auto_reward_credit_summary"""
    auto_reward_rule_id: Optional[str] = None
    accumulated_type: Optional[str] = None
    is_accumulated: Optional[bool] = None
    credit_threshold: Optional[str] = None
    credit_value: Optional[str] = None
    triggered: Optional[bool] = None
    calculate_credit_value: Optional[str] = None
    auto_reward_balance: Optional[str] = None


class Member_Point_SummaryConfig(BaseModel):
    """Configuration model for member_point_summary"""
    pending_days: Optional[int] = None
    earned_points: Optional[int] = None
    order_created_by: Optional[str] = None
    order_type: Optional[str] = None


class Payment_SlipsItem(BaseModel):
    """Item model for payment_slips"""
    text: Optional[str] = None
    owner_id: Optional[str] = None
    trackable_id: Optional[str] = None
    trackable_type: Optional[str] = None
    is_private: Optional[bool] = None
    is_last: Optional[bool] = None
    owner_type: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None


class Order_Items_Stock_TagItem(BaseModel):
    """Item model for order_items_stock_tag"""
    product_id: Optional[str] = None
    """ID of the product"""
    sku_id: Optional[str] = None
    """ID of the SKU"""
    order_item_id: Optional[str] = None
    """ID of the order item"""
    stock_tag: Optional[Union[Literal['REDUCE_FAILED', 'INCREASE_FAILED'], str]] = None
    """Stock tag for the order item"""

class Order(BaseModel):
    id: Optional[str] = None
    """Order ID 訂單ID"""
    order_number: Optional[str] = None
    """Order Number 訂單號碼"""
    system_order_number: Optional[str] = None
    """系统生成的訂單號"""
    merchant_order_number: Optional[str] = None
    """店家自定義訂單號 (會根據rollout_key選擇用哪個order_number)"""
    status: Optional[Union[Literal['temp', 'pending', 'removed', 'confirmed', 'completed', 'cancelled'], str]] = None
    """Order Status 訂單狀態  -  網店訂單 Status allows:  temp 暫存狀態  pending 處理中  removed 已刪除  confirmed 已確認  completed 已完成  cancelled 已取消    POS 訂單 Status allows:  confirmed 已確認  completed 已完成  cancelled 已取消"""
    is_guest_checkout: Optional[bool] = None
    """是否為訪客結帳"""
    order_remarks: Optional[str] = None
    """Order Remarks 訂單備註"""
    order_payment: Optional[OrderPayment] = None
    order_delivery: Optional[OrderDelivery] = None
    delivery_address: Optional[OrderDeliveryAddress] = None
    delivery_data: Optional[OrderDeliveryData] = None
    customer_id: Optional[str] = None
    """Cutomer ID 顧客ID"""
    customer_name: Optional[str] = None
    """Customer's Name 顧客姓名"""
    customer_email: Optional[str] = None
    """Customer's Email 顧客Email"""
    customer_phone: Optional[str] = None
    """Customer's Phone 顧客電話"""
    customer_phone_country_code: Optional[str] = None
    """Customer's Phone Country Code 顧客電話國碼"""
    customer_info: Optional[OrderCustomerInfo] = None
    currency_iso: Optional[str] = None
    """Currency ISO (ISO-4217) ISO 4217 貨幣代碼"""
    subtotal: Optional[Money] = None
    order_discount: Optional[Money] = None
    user_credit: Optional[Money] = None
    total_tax_fee: Optional[Money] = None
    total: Optional[Money] = None
    order_points: Optional[int] = None
    """Points used 會員點數使用"""
    order_points_to_cash: Optional[int] = None
    """Discounted by the points used 會員點數折抵金額"""
    invoice: Optional[OrderInvoice] = None
    invoices: Optional[List[InvoicesItem]] = None
    """Invoices Info 發票資訊（包含 EC、POS）"""
    subtotal_items: Optional[List[OrderItem]] = None
    promotion_items: Optional[List[OrderPromotionItem]] = None
    custom_data: Optional[List[Dict[str, Any]]] = None
    """Customized Order Fields 客製化欄位 - *欲使用此欄位請先至商店後台>訂單設定>自訂訂單欄位 進行設定"""
    custom_discount_items: Optional[List[OrderItem]] = None
    ref_order_id: Optional[str] = None
    """For third party custom order id 可供儲存第三方訂單ID"""
    ref_customer_id: Optional[str] = None
    """For third party custom customer id 可供儲存第三方顧客ID"""
    agent: Optional[OrderAgent] = None
    parent_order_id: Optional[str] = None
    """Parent Order ID 拆單後之母訂單ID"""
    child_order_ids: Optional[List[str]] = None
    """Child Order ID 拆單後之子訂單ID"""
    split_at: Optional[str] = None
    """Order Split Time 拆單時間"""
    confirmed_at: Optional[str] = None
    """Order Confirmed Time 訂單確認時間 (如尚未確認則顯示null)"""
    updated_at: Optional[str] = None
    """Order Updated Time 訂單更新時間 *UTC Time"""
    created_at: Optional[str] = None
    """Order Created Time 訂單創造日期 *UTC Time"""
    edited_at: Optional[str] = None
    """Order Edit Time 訂單修改日期 *UTC Time"""
    completed_at: Optional[str] = None
    """Order Completed Time 訂單完成日期 *UTC Time"""
    skip_fulfillment: Optional[bool] = None
    """Is order skipping fulfillment? 訂單是否略過“扣減庫存”"""
    utm_data: Optional[UtmData] = None
    ga_tracked: Optional[bool] = None
    """Is tracked by GA? 是否使用GA追蹤"""
    order_comments: Optional[List[Order_CommentsItem]] = None
    """Customer Comments 顧客通訊內容"""
    order_notes: Optional[List[Order_NotesItem]] = None
    """Order Notes 訂單備註"""
    created_by: Optional[Union[Literal['openapi', 'admin', 'shop', 'shop_crm', 'pos', 'sc', 'mc', 'import'], str]] = None
    """Channel that created the order 建立訂單的渠道"""
    agent_id: Optional[str] = None
    """Agent ID that created the order 代理建立訂單的操作者 ID  Only provided when include_fields contains 'agent_id'  僅於include_fields傳入 'agent_id' 時提供"""
    affiliate_data: Optional[Dict[str, Any]] = None
    """Affiliate Data 聯屬網絡營銷數據"""
    default_warehouse_id: Optional[str] = None
    """The default warehouse ID of the created_by_channel of the order. If the created_by_channel is blank, this field will be the default warehouse ID of the online channel.  訂單 created_by_channel 預設的倉庫 ID。如果 created_by_channel 為空，則此欄位將是 online channel 的 default_warehouse_id。"""
    channel: Optional[ChannelConfig] = None
    """Channel 渠道"""
    applied_tax_info: Optional[Applied_Tax_InfoConfig] = None
    """Applied Tax Info 稅務信息"""
    auto_reward_credit_summary: Optional[Auto_Reward_Credit_SummaryConfig] = None
    """訂單回饋購物金資訊"""
    member_point_summary: Optional[Member_Point_SummaryConfig] = None
    """訂單回饋點數資訊"""
    payment_slips: Optional[List[Payment_SlipsItem]] = None
    """Payment Slips 付款單"""
    type: Optional[Union[Literal['general', 'preorder', 'return', 'exchange'], str]] = None
    """Order type 訂單類型  The field is only available for POS orders (created_by: pos)  此欄位僅適用於POS訂單 (created_by: pos) - general: 一般訂單  - preorder: 預訂單  - return: 退貨單  - exchange: 換貨單"""
    affiliate_campaign: Optional[OrderCampaignItem] = None
    order_source: Optional[OrderSource] = None
    tags: Optional[List[str]] = None
    """Order tags 商品標籤"""
    inclusive_tax_info: Optional[Dict[str, Any]] = None
    """inclusive tax information 內含稅信息"""
    product_subscription_period: Optional[int] = None
    """Product Subscription Period 定期購期數"""
    allow_customer_cancel: Optional[bool] = None
    """Allow Customer Cancel 允許顧客取消訂單"""
    order_items_stock_tag: Optional[List[Order_Items_Stock_TagItem]] = None
    """Order items stock tag to indicate increasing or reducing stock failed  If there is no stock error, the field value will be null  Only provided when order_decoupling_product_revamp key is enabled  訂單商品庫存標籤，用來標示庫存增加或減少失敗  若沒有庫存錯誤，則此欄位值為 null  僅於order_decoupling_product_revamp key啟用才會顯示"""