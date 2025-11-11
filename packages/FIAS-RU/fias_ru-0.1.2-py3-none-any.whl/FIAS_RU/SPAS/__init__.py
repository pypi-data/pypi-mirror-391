"""
FIAS_RU/FIAS_RU/SPAS/__init__.py
"""

from .client import SPAS
from .models import (
    AddressType,
    AddressItem,
    SearchHint,
    AddressDetails,
    AddressObject,
    StructuredAddress,
)

__all__ = [
    "SPAS",
    "AddressType",
    "AddressItem",
    "SearchHint",
    "AddressDetails",
    "AddressObject",
    "StructuredAddress",
]