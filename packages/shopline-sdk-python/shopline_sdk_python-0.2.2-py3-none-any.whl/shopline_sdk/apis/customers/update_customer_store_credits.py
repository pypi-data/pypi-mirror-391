from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.not_found_error import NotFoundError
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.store_credit import StoreCredit
from shopline_sdk.models.unauthorized_error import UnauthorizedError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError

class Params(BaseModel):
    """查询参数模型"""
    excludes: Optional[List[str]] = Field(default=None, alias="excludes[]")
    """Exclude certain parameters in the response
      結果要排除哪些參數"""
    fields: Optional[List[str]] = Field(default=None, alias="fields[]")
    """Only show certain parameters in the response
       結果只顯示哪些參數"""

class Body(BaseModel):
    """请求体模型"""
    value: int
    """Credits to be added or deducted
      增加或減除金額
      -
      *Number can be -999999~999999"""
    remarks: str
    """Reason for adding or deducting credits
      增加或減除購物金原因
      -
      * Limit to max 50 characters"""
    expires_at: Optional[str] = None
    """Validity Period
      有效期限
      * Date cannot be in the past 
      * Date should be within 9999 days from now"""
    email_target: Optional[int] = None
    """Notification with Email
      是否發送email通知
      Only applicable for addition
      僅適用於增加
      -
       1=NOT_SEND全部不送
       3=SEND_TO_ALL全部都送"""
    sms_notification_target: Optional[int] = None
    """Notification with SMS
      是否發送簡訊通知
      Only applicable for addition
      僅適用於增加
      -
       1=NOT_SEND全部不送
       2=SEND_VERIFIED只送手機驗證過的
       3=SEND_TO_ALL全部都送"""
    replace: Optional[bool] = None
    """To replace all store credits with the current value
      以此金額替代之前所有購物金"""
    type: Optional[Union[Literal['manual_credit', 'welcome_credit', 'birthday_credit', 'auto_reward', 'applied_credit', 'user_credit_expired', 'welcome_member_referral_credit', 'member_referral_credit', 'member_info_quick_completion_credit', 'order_split_revert', 'product_review_reward', 'return_order_revert', 'order_edit_revert'], str]] = None
    """Store credit type
       購物金類型
       * `manual_credit`
       Manually assign store credit(s) to specific member
       手動發送購物金給指定會員
       * `welcome_credit`
       Auto assign welcome credits to new registered members
       發送購物金鼓勵顧客註冊會員和進行第一次購物
       * `birthday_credit`
       Auto assign store credits to members as gifts on their birthday
       於會員的生日自動發送購物金作為生日禮物
       * `auto_reward`
       Auto reward customers with credits when they meet a minimum amount of purchase
       當訂單達到最低金額時自動發送購物金給會員
       * `applied_credit`
       Applied user credits when placing an order
       在下訂單時已折抵的購物金
       * `user_credit_expired`
       Expired user credits
       已過期的購物金
       * `welcome_member_referral_credit`
       Referral will get store credits after sign up
       新會員透過推薦連結註冊成為會員即可獲得購物金
       * `member_referral_credit`
       Referrer will get the reward after an order from referral is completed
       新顧客註冊後在訂單轉為「已完成」後，推薦人即可獲得購物金
       * `member_info_quick_completion_credit`
       Member info reward credit
       會員資料獎賞購物金
       * `order_split_revert`
       Order split revert credit
       訂單拆單回補購物金
       * `product_review_reward`
       Product review reward credit
       商品評價獎賞購物金
       * `return_order_revert`
       Return order revert credit
       退貨單回補購物金
       * `order_edit_revert`
       Order edit revert credit
       訂單編輯回補購物金"""
    performer_id: Optional[str] = None
    """Performer ID
      操作者ID"""
    performer_type: Optional[Union[Literal['User', 'Agent'], str]] = None
    """Performer Type
      操作者類型"""

async def call(
    session: aiohttp.ClientSession, id: str, params: Optional[Params] = None, body: Optional[Body] = None
) -> StoreCredit:
    """
    Update Customer Store Credits
    
    To update customer store credits with open API
    使用open API更新顧客購物金
    
    Path: POST /customers/{id}/store_credits
    """
    # 构建请求 URL
    url = f"customers/{id}/store_credits"

    # 构建查询参数
    query_params = {}
    if params:
        params_dict = params.model_dump(exclude_none=True, by_alias=True)
        for key, value in params_dict.items():
            if value is not None:
                query_params[key] = value

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.post(
        url, params=query_params, json=json_data, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            if response.status == 401:
                error = UnauthorizedError(**error_data)
                raise ShoplineAPIError(
                    status_code=401,
                    error=error
                )
            if response.status == 404:
                error = NotFoundError(**error_data)
                raise ShoplineAPIError(
                    status_code=404,
                    error=error
                )
            if response.status == 422:
                error = UnprocessableEntityError(**error_data)
                raise ShoplineAPIError(
                    status_code=422,
                    error=error
                )
            if response.status == 500:
                error = ServerError(**error_data)
                raise ShoplineAPIError(
                    status_code=500,
                    error=error
                )
            # 默认错误处理
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return StoreCredit(**response_data)