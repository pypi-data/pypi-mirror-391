"""Shopline API 数据模型 - MerchantKyc"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal

# 导入相关模型
from .corporate_info import CorporateInfo
from .individual_info import IndividualInfo


class MerchantKyc(BaseModel):
    type: Optional[Union[Literal['individual', 'corporate'], str]] = None
    """entity type 實體類型"""
    bank_code: Optional[str] = None
    """Bank code 銀行代碼"""
    bank_account: Optional[str] = None
    """Bank account 銀行帳戶"""
    bank_account_name: Optional[str] = None
    """Bank account holder name 銀行戶名"""
    individual_info: Optional[Union[IndividualInfo, Any]] = None
    """Information for individual entities 個人資料，type為corporate時為null"""
    corporate_info: Optional[Union[CorporateInfo, Any]] = None
    """Information for corporate entities 公司資料，type為individual時為null"""