"""Shopline API 数据模型 - TokenScopes"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from typing_extensions import Literal


class TokenScopes(BaseModel):
    scopes: Optional[Dict[str, Dict[str, Any]]] = None
    """All scopes available"""