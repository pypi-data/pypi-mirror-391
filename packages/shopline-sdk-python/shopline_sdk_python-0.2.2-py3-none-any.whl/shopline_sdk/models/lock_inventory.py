"""Shopline API 数据模型 - LockInventory"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class LockInventory(BaseModel):
    items: Optional[List['LockInventory']] = None