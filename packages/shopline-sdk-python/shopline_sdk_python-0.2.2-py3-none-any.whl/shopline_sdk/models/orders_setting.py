"""Shopline API 数据模型 - OrdersSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal



class Facebook_MessengingConfig(BaseModel):
    """Configuration model for facebook_messenging"""
    status: Optional[str] = None

class OrdersSetting(BaseModel):
    invoice_activation: Optional[str] = None
    current_invoice_service_provider: Optional[str] = None
    facebook_messenging: Optional[Facebook_MessengingConfig] = None
    invoice: Optional[Dict[str, Any]] = None
    invoice_tradevan: Optional[Dict[str, Any]] = None
    no_duplicate_uniform_invoice: Optional[bool] = None
    enabled_location_id: Optional[bool] = None
    """Enable "Location ID Setting" in Admin  後台啟用「儲位編號設定」功能"""
    customer_cancel_order: Optional[Dict[str, Any]] = None
    customer_return_order: Optional[Dict[str, Any]] = None
    default_out_of_stock_reminder: Optional[bool] = None
    """Enable "Out-Of-Stock Reminder" in Admin  啟用「商品預設缺貨提醒」功能"""