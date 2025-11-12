"""Shopline API 数据模型 - StoreCredit"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .money import Money


class StoreCredit(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    """Record ID 紀錄 ID"""
    customer_id: Optional[str] = None
    """Customer ID 顧客 ID"""
    credit_balance: Optional[int] = None
    """Credit balance after this record 此紀錄後的購物金餘額"""
    remarks: Optional[str] = None
    """Credit Change Reason	 購物金更動原因"""
    value: Optional[int] = None
    """Credit Movement 購物金款項"""
    end_at: Optional[str] = None
    """Expiry Date 到期日"""
    performer_id: Optional[str] = None
    """ID of the staff who created this record 創建紀錄的管理員的ID"""
    performer_name: Optional[str] = None
    """Staff who created this record 創建紀錄的管理員"""
    fulfillment_balance: Optional[int] = None
    """Fulfillment Balance 購物金餘額"""
    type: Optional[Union[Literal['manual_credit', 'welcome_credit', 'birthday_credit', 'auto_reward', 'applied_credit', 'user_credit_expired', 'welcome_member_referral_credit', 'member_referral_credit', 'order_split_revert', 'member_info_quick_completion_credit', 'product_review_reward', 'return_order_revert', 'order_edit_revert'], str]] = None
    """Store credit type 購物金類型  ----  manual_credit: 手動增減購物金（店家手動發送、回補來自取消訂單/退貨訂單）  welcome_credit: 新加入會員購物金  birthday_credit: 生日購物金  auto_reward: 購物金回饋  applied_credit: 套用購物金在訂單  user_credit_expired: 購物金過期  welcome_member_referral_credit: 透過推薦連結註冊成功  member_referral_credit: 推薦新顧客進行消費  order_split_revert: 回補購物金（來自拆單）  product_review_reward: 商品評價獎賞  member_info_quick_completion_credit: 會員資料獎賞  return_order_revert: 退貨單回補購物金  order_edit_revert: 訂單編輯回補購物金"""
    created_at: Optional[str] = None
    """Record creation date 創建紀錄日期"""
    customer_ref_user_id: Optional[str] = None
    """Third party custom customer id 第三方儲存之顧客ID"""
    status: Optional[Union[Literal['active', 'removed', 'expired', 'used', 'redeemed'], str]] = None
    """Status 購物金狀態"""
    is_redeem: Optional[bool] = None
    """Whether the store credit is redeemed  購物金是否已經被兌換"""
    order_id: Optional[str] = None
    """The ID of the order where the store credit earned from 賺取購物金的訂單的ID"""
    value_dollar: Optional[Money] = None
    user_credit_rule_id: Optional[str] = None
    """The ID of user_credit_rule"""
    order_number: Optional[str] = None
    """Order number 訂單號碼"""
    merchant_order_number: Optional[str] = None
    """The order number set by the merchant 店家自定義訂單號"""
    order_created_by: Optional[str] = None
    """Order created by 此訂單的建立者"""