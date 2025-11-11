"""
FIAS_RU - Простой и надёжный SDK для работы с ФИАС API

"""

__version__ = "0.1.2"
__author__ = "Eclips team"
__email__ = "develop@eclips-team.ru"

# Импорты базовых классов
from .SPAS import (
    AddressType,
    AddressItem,
    SearchHint,
    AddressDetails,
    AddressObject,
    StructuredAddress,
    SPAS,
)

# Импорты исключений
from .SPAS.exceptions import (
    FIASError,
    FIASValidationError,
    FIASAPIError,
    FIASNetworkError,
    FIASTimeoutError,
    FIASNotFoundError,
)

__all__ = [
    # Версия
    "__version__",
    "__author__",
    "__email__",

    # Модели
    "AddressType",
    "AddressItem",
    "SearchHint",
    "AddressDetails",
    "AddressObject",
    "StructuredAddress",

    # Клиент
    "SPAS",

    # Исключения
    "FIASError",
    "FIASValidationError",
    "FIASAPIError",
    "FIASNetworkError",
    "FIASTimeoutError",
    "FIASNotFoundError",
]