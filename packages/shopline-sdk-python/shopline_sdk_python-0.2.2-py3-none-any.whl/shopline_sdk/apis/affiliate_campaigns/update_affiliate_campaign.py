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


class PartnerInfoSchema(BaseModel):
    """Partner info
    合作夥伴資訊"""
    name: Optional[str] = None
    """Partner name
      合作夥伴名稱"""
    email: Optional[str] = None
    """Partner email
      合作夥伴 Email"""

class Body(BaseModel):
    """请求体模型"""
    name: Optional[str] = None
    """Affiliate Campaign Name
      推薦活動名稱"""
    promotion_id: Optional[str] = None
    """Promotion Id
      套用優惠折扣 ID"""
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
    partner_info: Optional[PartnerInfoSchema] = None
    """Partner info
      合作夥伴資訊"""
    campaign_products: Optional[List[CampaignProduct]] = None
    """Add item without id param to array to create new campaign product.
       Remove item from array to delete campaign product.
       Update item is not allowed.
      
       藉由新增不含 id 的物件到陣列中，即可新增新的 Campaign Product。
       從陣列中移除物件即可刪除該 Campaign Product。
       不可更新任何已存在的 Campaign Product 其資料。"""

async def call(
    session: aiohttp.ClientSession, id: str, body: Optional[Body] = None
) -> AffiliateCampaign:
    """
    Update Affiliate Campaign
    
    To update affiliate campaign.
    更新推薦活動。
    
    Path: PUT /affiliate_campaigns/{id}
    """
    # 构建请求 URL
    url = f"affiliate_campaigns/{id}"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 构建请求体
    json_data = body.model_dump(exclude_none=True) if body else None

    # 发起 HTTP 请求
    async with session.put(
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