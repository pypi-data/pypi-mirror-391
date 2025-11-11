"""
FIAS_RU/FIAS_RU/SPAS/exceptions.py

Кастомные исключения для FIAS SDK
"""


class FIASError(Exception):
    """Базовое исключение для всех ошибок FIAS SDK"""
    pass


class FIASValidationError(FIASError):
    """Ошибка валидации входных данных"""
    pass


class FIASAPIError(FIASError):
    """Ошибка API (5xx, ошибки сервера)"""
    pass


class FIASNetworkError(FIASError):
    """Сетевая ошибка (проблемы с соединением)"""
    pass


class FIASTimeoutError(FIASError):
    """Таймаут запроса"""
    pass


class FIASNotFoundError(FIASError):
    """Объект не найден (404)"""
    pass