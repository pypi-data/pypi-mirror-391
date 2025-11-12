"""Shopline API 数据模型 - ReturnOrderRefData"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class ReturnOrderRefData(BaseModel):
    return_order_revamp: Optional[str] = None
    """Return order revamp feature flag"""