from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.affiliate_campaign import AffiliateCampaign
from shopline_sdk.models.campaign_product import CampaignProduct
from shopline_sdk.models.server_error import ServerError
from shopline_sdk.models.unprocessable_entity_error import UnprocessableEntityError


class CampaignProductsSchema(BaseModel):
    """Model for campaign_products"""
    product_id: Optional[str] = None
    affiliate_percentage: Optional[float] = None
    affiliate_amount: Optional[Dict[str, Any]] = None

class Body(BaseModel):
    """请求体模型"""
    name: str
    """Affiliate Campaign Name
      推薦活動名稱"""
    reward_type: Optional[str] = None
    """Reward type
      訂單回饋類型"""
    promotion_id: Optional[str] = None
    """Promotion Id
      套用優惠折扣 ID"""
    code: str
    """Affiliate code
      推薦代碼"""
    start_at: Optional[str] = None
    """Affiliate campaign start time
      推薦活動開始時間
      -
      *UTC Time"""
    end_at: Optional[str] = None
    """Affiliate campaign end time
      推薦活動結束時間
      -
      *UTC Time"""
    remarks_translations: Optional[Dict[str, Any]] = None
    """Remarks translations
      顯示於 KOL Hub 的條款說明"""
    apply_on: Optional[Union[Literal['order', 'product'], str]] = None
    """Apply on order or product
      套用於訂單或商品"""
    apply_method: Optional[Union[Literal['all', 'product'], str]] = None
    """Apply method
       套用方式:
       - all: 全部
       - item: 逐筆設定"""
    affiliate_percentage: Optional[float] = None
    """Affiliate percentage
      分潤百分比"""
    affiliate_amount: Optional[Dict[str, Any]] = None
    """Affiliate amount
      分潤固定金額"""
    condition_min_amount: Optional[Dict[str, Any]] = None
    """The threshold amount (for order level)
      門檻金額 (for order level)"""
    campaign_products: Optional[CampaignProductsSchema] = None

async def call(
    session: aiohttp.ClientSession, body: Optional[Body] = None
) -> AffiliateCampaign:
    """
    Create Affiliate Campaign
    
    To create affiliate campaign.
    建立推薦活動。
    
    Path: POST /affiliate_campaigns
    """
    # 构建请求 URL
    url = "affiliate_campaigns"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.post(
        url, json=json_data, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
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
        return AffiliateCampaign(**response_data)