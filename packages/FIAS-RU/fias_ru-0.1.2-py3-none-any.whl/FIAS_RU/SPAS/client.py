"""
FIAS_RU/FIAS_RU/SPAS/client.py
"""

from typing import List, Optional, Union
import os
import re
import logging
from functools import wraps
from .base import FIASClient
from .models import AddressType, AddressItem, SearchHint, AddressDetails
from .exceptions import (
    FIASValidationError,
    FIASAPIError,
    FIASTimeoutError,
    FIASNetworkError
)

logger = logging.getLogger(__name__)

# Константы
DEFAULT_BASE_URL = "https://fias-public-service.nalog.ru"
GUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
CADASTRAL_PATTERN = re.compile(r'^\d{2}:\d{2}:\d{6,7}:\d+$')


def auto_retry(func):
    """Декоратор для автоматических повторов с логированием"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        max_attempts = self.max_retries
        for attempt in range(max_attempts):
            try:
                return func(self, *args, **kwargs)
            except (FIASTimeoutError, FIASNetworkError) as e:
                if attempt < max_attempts - 1:
                    logger.warning(f"Попытка {attempt + 1}/{max_attempts} провалилась, повтор...")
                else:
                    raise
            except FIASAPIError:
                raise  # Не повторяем при API ошибках
    return wrapper


class SPAS(FIASClient):
    """
    🚀 Максимально простой клиент для работы с ФИАС

    Быстрый старт:
        >>> from FIAS_RU import SPAS
        >>>
        >>> # Вариант 1: Автоматически из переменных окружения
        >>> spas = SPAS()  # Использует FIAS_TOKEN из env
        >>>
        >>> # Вариант 2: Явно указать токен
        >>> spas = SPAS(token="your_token")
        >>>
        >>> # Вариант 3: Полная настройка
        >>> spas = SPAS(base_url="https://...", token="...")
        >>>
        >>> # Поиск (автоопределение типа)
        >>> address = spas.search("Москва, Тверская 1")
        >>> address = spas.search("77000000000000000000000")  # по GUID
        >>> address = spas.search("77:01:0001001:1")  # по кадастру
        >>> address = spas.search(123456)  # по ID
        >>>
        >>> # Автокомплит
        >>> hints = spas.autocomplete("Москва, Тв")
        >>>
        >>> # Работа с результатами
        >>> print(address.full_name)
        >>> print(address.postal_code)  # Быстрый доступ к деталям
        >>> print(address.oktmo)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        default_address_type: AddressType = AddressType.ADMINISTRATIVE,
        **kwargs
    ):
        """
        Инициализация клиента SPAS

        Args:
            base_url: URL API (по умолчанию: публичный API ФНС)
            token: Токен авторизации (по умолчанию: из FIAS_TOKEN env)
            timeout: Таймаут запросов в секундах
            max_retries: Количество повторных попыток
            default_address_type: Тип адреса по умолчанию
            **kwargs: Дополнительные параметры (max_connections, rate_limit и т.д.)

        Raises:
            FIASValidationError: Если токен не указан и не найден в переменных окружения

        Examples:
            >>> # Минимальная конфигурация
            >>> spas = SPAS()  # Токен из FIAS_TOKEN
            >>>
            >>> # С явным токеном
            >>> spas = SPAS(token="your_token_here")
            >>>
            >>> # Полная конфигурация
            >>> spas = SPAS(
            ...     base_url="https://custom-api.com",
            ...     token="token",
            ...     timeout=60,
            ...     max_retries=5
            ... )
        """
        # Автоопределение URL
        if base_url is None:
            base_url = os.getenv("FIAS_BASE_URL", DEFAULT_BASE_URL)

        # Автоопределение токена
        if token is None:
            token = os.getenv("FIAS_TOKEN")
            if not token:
                raise FIASValidationError(
                    "Токен не найден! Укажите токен одним из способов:\n"
                    "1. SPAS(token='your_token')\n"
                    "2. Установите переменную окружения: export FIAS_TOKEN='your_token'\n"
                    "3. Создайте .env файл с FIAS_TOKEN=your_token"
                )

        super().__init__(base_url, timeout, **kwargs)
        self.token = token
        self.max_retries = max_retries
        self.default_address_type = default_address_type

        logger.info(f"SPAS клиент инициализирован: {base_url}")

    def _get_headers(self) -> dict:
        """Получить заголовки с токеном"""
        return {
            "accept": "application/json",
            "Content-Type": "application/json",
            "master-token": self.token  # ФИАС использует master-token header
        }

    def _handle_response(self, response, error_prefix: str = "Ошибка API"):
        """Обработка ответа с понятными сообщениями"""
        try:
            response.raise_for_status()
            return response.json()
        except Exception as e:
            status = getattr(response, 'status_code', None)

            # Красивые сообщения об ошибках
            if status == 403:
                raise FIASAPIError(
                    "❌ Доступ запрещён. Проверьте токен авторизации.\n"
                    "Получите токен на https://fias.nalog.ru/"
                )
            elif status == 404:
                return None  # Не найдено - это нормально
            elif status == 429:
                raise FIASAPIError("⏱️ Превышен лимит запросов. Подождите немного.")
            elif status in (500, 502, 503):
                raise FIASAPIError(f"🔧 Сервер временно недоступен ({status})")
            elif status == 408:
                raise FIASTimeoutError("⏰ Таймаут запроса. Попробуйте увеличить timeout")
            else:
                text = getattr(response, 'text', str(e))[:200]
                raise FIASNetworkError(f"{error_prefix} ({status}): {text}")

    def _detect_query_type(self, query: Union[str, int]) -> tuple:
        """
        🧠 Умное определение типа запроса

        Returns:
            (query_type, normalized_query)
            query_type: 'id' | 'guid' | 'cadastral' | 'string'
        """
        if isinstance(query, int):
            return ('id', query)

        if not isinstance(query, str):
            raise FIASValidationError(f"Запрос должен быть строкой или числом: {type(query)}")

        query = query.strip()

        # GUID
        if GUID_PATTERN.match(query):
            return ('guid', query)

        # Кадастровый номер
        if CADASTRAL_PATTERN.match(query):
            return ('cadastral', query)

        # ID (строка с числом)
        if query.isdigit():
            return ('id', int(query))

        # Обычная строка
        return ('string', query)

    # =================================================================
    # ГЛАВНЫЕ МЕТОДЫ (максимально простые)
    # =================================================================

    @auto_retry
    def search(
        self,
        query: Union[str, int],
        address_type: Optional[AddressType] = None
    ) -> Optional[AddressItem]:
        """
        🔍 Умный поиск - автоматически определяет тип запроса

        Args:
            query: Что искать (строка, ID, GUID, кадастровый номер)
            address_type: Тип адреса (по умолчанию из конфига)

        Returns:
            Найденный адрес или None

        Examples:
            >>> spas = SPAS()
            >>>
            >>> # Поиск по строке
            >>> addr = spas.search("Москва, Тверская 1")
            >>>
            >>> # Поиск по GUID
            >>> addr = spas.search("77000000-0000-0000-0000-000000000000")
            >>>
            >>> # Поиск по кадастровому номеру
            >>> addr = spas.search("77:01:0001001:1")
            >>>
            >>> # Поиск по ID
            >>> addr = spas.search(123456)
            >>> addr = spas.search("123456")  # Тоже работает
        """
        query_type, normalized_query = self._detect_query_type(query)
        address_type = address_type or self.default_address_type

        self.rate_limiter.acquire()

        try:
            # Роутинг по типу запроса
            if query_type == 'id':
                return self._search_by_id(normalized_query, address_type)
            elif query_type == 'guid':
                return self._search_by_guid(normalized_query, address_type)
            elif query_type == 'cadastral':
                return self._search_by_cadastral(normalized_query, address_type)
            else:  # string
                return self._search_by_string(normalized_query, address_type)

        except Exception as e:
            logger.error(f"Не удалось найти '{query}': {e}")
            raise

    def _search_by_string(self, query: str, address_type: AddressType) -> Optional[AddressItem]:
        """Поиск по строке"""
        if len(query) < 3:
            raise FIASValidationError("Минимальная длина запроса - 3 символа")

        response = self.sync_client.get(
            "/api/spas/v2.0/SearchAddressItem",
            params={"search_string": query, "address_type": address_type.value},
            headers=self._get_headers()
        )
        data = self._handle_response(response, f"Ошибка поиска '{query}'")
        return AddressItem(**data) if data else None

    def _search_by_id(self, object_id: int, address_type: AddressType) -> Optional[AddressItem]:
        """Поиск по ID"""
        response = self.sync_client.get(
            "/api/spas/v2.0/GetAddressItemById",
            params={"object_id": object_id, "address_type": address_type.value},
            headers=self._get_headers()
        )
        data = self._handle_response(response, f"Ошибка поиска ID={object_id}")
        addresses = data.get("addresses", []) if data else []
        return AddressItem(**addresses[0]) if addresses else None

    def _search_by_guid(self, guid: str, address_type: AddressType) -> Optional[AddressItem]:
        """Поиск по GUID"""
        response = self.sync_client.get(
            "/api/spas/v2.0/GetAddressItemByGuid",
            params={"object_guid": guid, "address_type": address_type.value},
            headers=self._get_headers()
        )
        data = self._handle_response(response, f"Ошибка поиска GUID={guid}")
        addresses = data.get("addresses", []) if data else []
        return AddressItem(**addresses[0]) if addresses else None

    def _search_by_cadastral(self, cadastral: str, address_type: AddressType) -> Optional[AddressItem]:
        """Поиск по кадастровому номеру"""
        response = self.sync_client.get(
            "/api/spas/v2.0/GetAddressItemByCadastralNumber",
            params={"cadastral_number": cadastral, "address_type": address_type.value},
            headers=self._get_headers()
        )
        data = self._handle_response(response, f"Ошибка поиска кадастра={cadastral}")
        addresses = data.get("addresses", []) if data else []
        return AddressItem(**addresses[0]) if addresses else None

    @auto_retry
    def autocomplete(
        self,
        partial_address: str,
        limit: int = 10,
        address_type: Optional[AddressType] = None,
        up_to_level: Optional[int] = None
    ) -> List[SearchHint]:
        """
        💡 Автокомплит адреса (как в Яндекс/Google картах)

        Args:
            partial_address: Неполный адрес (минимум 1 символ)
            limit: Максимум подсказок (по умолчанию 10)
            address_type: Тип адреса
            up_to_level: До какого уровня искать

        Returns:
            Список подсказок для автокомплита

        Examples:
            >>> spas = SPAS()
            >>>
            >>> # Простой автокомплит
            >>> hints = spas.autocomplete("Москва, Тв")
            >>> for hint in hints:
            ...     print(hint.full_name)
            >>>
            >>> # С ограничением результатов
            >>> hints = spas.autocomplete("Санкт", limit=5)
            >>>
            >>> # До определённого уровня (например, только улицы)
            >>> hints = spas.autocomplete("Москва, Тверская", up_to_level=7)
        """
        if not partial_address or len(partial_address.strip()) < 1:
            raise FIASValidationError("Минимальная длина запроса - 1 символ")

        address_type = address_type or self.default_address_type
        self.rate_limiter.acquire()

        try:
            payload = {
                "searchString": partial_address.strip(),
                "addressType": address_type.value
            }
            if up_to_level is not None:
                payload["upToLevel"] = up_to_level

            response = self.sync_client.post(
                "/api/spas/v2.0/GetAddressHint",
                json=payload,
                headers=self._get_headers()
            )
            data = self._handle_response(response, f"Ошибка автокомплита '{partial_address}'")
            hints = [SearchHint(**hint) for hint in data.get("hints", [])]

            return hints[:limit]
        except Exception as e:
            logger.error(f"Автокомплит провалился для '{partial_address}': {e}")
            raise

    @auto_retry
    def get_regions(self) -> List[AddressItem]:
        """
        🗺️ Получить все регионы РФ

        Returns:
            Список всех регионов

        Example:
            >>> spas = SPAS()
            >>> regions = spas.get_regions()
            >>> for region in regions[:5]:
            ...     print(f"{region.region_code}: {region.full_name}")
        """
        self.rate_limiter.acquire()

        try:
            response = self.sync_client.get(
                "/api/spas/v2.0/GetRegions",
                headers=self._get_headers()
            )
            data = self._handle_response(response, "Ошибка получения регионов")
            return [AddressItem(**addr) for addr in data.get("addresses", [])]
        except Exception as e:
            logger.error(f"Не удалось получить регионы: {e}")
            raise

    @auto_retry
    def get_details(self, address: Union[AddressItem, int]) -> Optional[AddressDetails]:
        """
        ℹ️ Получить детали адреса (ОКТМО, ИФНС, почтовый индекс и т.д.)

        Args:
            address: AddressItem или object_id

        Returns:
            Детали адреса

        Examples:
            >>> spas = SPAS()
            >>>
            >>> # Вариант 1: Передать AddressItem
            >>> addr = spas.search("Москва, Тверская 1")
            >>> details = spas.get_details(addr)
            >>>
            >>> # Вариант 2: Передать ID напрямую
            >>> details = spas.get_details(123456)
            >>>
            >>> print(details.postal_code)
            >>> print(details.oktmo)
        """
        object_id = address.object_id if isinstance(address, AddressItem) else address

        if not isinstance(object_id, int) or object_id <= 0:
            raise FIASValidationError(f"ID должен быть положительным числом: {object_id}")

        self.rate_limiter.acquire()

        try:
            response = self.sync_client.get(
                "/api/spas/v2.0/GetDetails",
                params={"object_id": object_id},
                headers=self._get_headers()
            )
            data = self._handle_response(response, f"Ошибка получения деталей ID={object_id}")

            if data and "address_details" in data:
                return AddressDetails(**data["address_details"])
            return None
        except Exception as e:
            logger.error(f"Не удалось получить детали {object_id}: {e}")
            raise

    # =================================================================
    # УДОБНЫЕ АЛИАСЫ
    # =================================================================

    def find(self, query: Union[str, int], **kwargs) -> Optional[AddressItem]:
        """Алиас для search()"""
        return self.search(query, **kwargs)

    def complete(self, partial: str, **kwargs) -> List[SearchHint]:
        """Алиас для autocomplete()"""
        return self.autocomplete(partial, **kwargs)

    # =================================================================
    # CONTEXT MANAGER
    # =================================================================

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __repr__(self):
        return f"<SPAS(base_url='{self.base_url}', token='***')>"