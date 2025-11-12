"""Shopline API 数据模型 - OrderInvoice"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class OrderInvoice(BaseModel):
    tax_id: Optional[str] = None
    """Tax ID Number 發票統一編號"""
    mailing_address: Optional[str] = None
    """Mailing Address 發票地址"""
    invoice_type: Optional[Union[Literal['0', '1', '2'], str]] = None
    """Invoice Type 發票種類 -  0 電子發票  1  捐贈發票  *2 紙本發票（公司戶紙本發票/二聯式發票） -  當 tax_id 有值時，為「公司戶紙本發票」；當 tax_id 沒有值時，則為「二聯式發票」"""
    buyer_name: Optional[str] = None
    """Buyer Name 發票抬頭"""
    carrier_type: Optional[Union[Literal['0', '1', '2'], str]] = None
    """Carrier Type 載具類型 -  0 會員載具  1 手機條碼  *2 自然人憑證條碼"""
    carrier_number: Optional[str] = None
    """Carrier Number 載具號碼"""
    n_p_o_b_a_n: Optional[str] = None
    """發票捐贈愛心碼"""
    invoice_tax_type: Optional[Union[Literal['1', '2', '5'], str]] = None
    """Invoice Tax Type 發票税別 -  1 應稅  2 零稅率-非經海關出口  *5 零稅率-經海關出口"""
    invoice_number: Optional[str] = None
    """Invoice Number 發票號碼"""
    invoice_status: Optional[Union[Literal['active', 'cancel'], str]] = None
    """Invoice status 發票狀態 -  active 已開立  cancel 已作廢"""
    invoice_date: Optional[str] = None
    """Invoice Date 發票開立日期"""
    invoice_cancelled_at: Optional[str] = None
    """Invoice Cancelled Date 發票作廢日期"""