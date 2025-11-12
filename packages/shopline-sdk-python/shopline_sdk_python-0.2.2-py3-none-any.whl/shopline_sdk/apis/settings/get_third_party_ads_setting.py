from typing import Any, Dict, List, Optional, Union
import aiohttp
from pydantic import BaseModel, ValidationError, Field
from typing_extensions import Literal

# 导入异常类
from shopline_sdk.exceptions import ShoplineAPIError

# 导入需要的模型
from shopline_sdk.models.third_party_ads_setting import ThirdPartyAdsSetting

async def call(
    session: aiohttp.ClientSession
) -> ThirdPartyAdsSetting:
    """
    Get Third Party Ads Setting
    
    To retrieve the setting of third party ads
    獲取第三方廣告設定
    
    Path: GET /settings/third_party_ads
    """
    # 构建请求 URL
    url = "settings/third_party_ads"

    # 构建请求头
    headers = {"Content-Type": "application/json"}

    # 发起 HTTP 请求
    async with session.get(
        url, headers=headers
    ) as response:
        if response.status >= 400:
            error_data = await response.json()
            raise ShoplineAPIError(
                status_code=response.status,
                **error_data
            )
        response_data = await response.json()

        # 验证并返回响应数据
        return ThirdPartyAdsSetting(**response_data)