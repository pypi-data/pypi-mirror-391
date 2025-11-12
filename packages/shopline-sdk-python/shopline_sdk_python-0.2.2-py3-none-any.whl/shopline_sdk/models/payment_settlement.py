"""Shopline API 数据模型 - PaymentSettlement"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Sdk_ParamsConfig(BaseModel):
    """Configuration model for sdk_params"""
    settleRequestNo: Optional[str] = None
    tradeSettlementBatchNo: Optional[str] = None
    status: Optional[str] = None
    nextAction: Optional[Dict[str, Any]] = None
    paymentError: Optional[Dict[str, Any]] = None
    """Fail Reason of applying 申請失敗原因"""


class ResultConfig(BaseModel):
    """Configuration model for result"""
    settleRequestNo: Optional[str] = None
    tradeSettlementBatchNo: Optional[str] = None
    merchantId: Optional[str] = None
    sceneType: Optional[str] = None
    batchApplyTime: Optional[str] = None
    batchFinishTime: Optional[str] = None
    status: Optional[str] = None
    paymentError: Optional[Dict[str, Any]] = None
    """Fail of settlement 結帳失敗原因"""

class PaymentSettlement(BaseModel):
    id: Optional[str] = None
    """Payment Settlement ID 刷卡機結帳 ID"""
    channel_id: Optional[str] = None
    """Channel ID  Channel ID"""
    terminal_id: Optional[str] = None
    """Terminal ID 刷卡機 ID"""
    status: Optional[Union[Literal['pending', 'completed', 'failed'], str]] = None
    """Status 結帳狀態"""
    created_at: Optional[str] = None
    """Created at 建立時間"""
    updated_at: Optional[str] = None
    """Updated at 更新時間"""
    sdk_params: Optional[Sdk_ParamsConfig] = None
    """SDK Params of applying settlement 申請結帳參數"""
    result: Optional[ResultConfig] = None
    """Settlement Result 結帳結果"""