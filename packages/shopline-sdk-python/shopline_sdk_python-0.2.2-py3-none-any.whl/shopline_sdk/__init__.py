"""
Shopline SDK for Python

A Python SDK for interacting with the Shopline OpenAPI.
"""

__version__ = "0.1.0"
__author__ = "Shopline"
__description__ = "Shopline OpenAPI on python implement. (From https://open-api.docs.shoplineapp.com)"

from .client import ShoplineAPIClient
from .exceptions import *

__all__ = [
    "ShoplineAPIClient",
    "__version__",
]