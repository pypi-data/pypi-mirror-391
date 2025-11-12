"""Shopline API 数据模型 - TaxSetting"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class TaxSetting(BaseModel):
    products_taxable: Optional[bool] = None
    """All Shops need Tax Collection 全店皆需收稅"""