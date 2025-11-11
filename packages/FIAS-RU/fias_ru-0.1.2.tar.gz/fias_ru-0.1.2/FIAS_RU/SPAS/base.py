"""
FIAS_RU/FIAS_RU/SPAS/base.py

"""

from typing import Optional
import httpx
import time
from threading import Lock
from collections import deque


class RateLimiter:
    """Простой rate limiter для предотвращения перегрузки API"""

    def __init__(self, max_requests: int = 100, time_window: float = 60.0):
        """
        Args:
            max_requests: Максимум запросов
            time_window: Временное окно в секундах
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = Lock()

    def acquire(self):
        """Ждём, пока не сможем сделать запрос"""
        with self.lock:
            now = time.time()

            # Удаляем старые записи
            while self.requests and self.requests[0] < now - self.time_window:
                self.requests.popleft()

            # Если превышен лимит, ждём
            if len(self.requests) >= self.max_requests:
                sleep_time = self.requests[0] + self.time_window - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    # Рекурсивно пробуем снова
                    return self.acquire()

            # Добавляем текущий запрос
            self.requests.append(now)


class FIASClient:
    """
    Улучшенный базовый клиент для HTTP запросов к ФИАС API

    Новые возможности:
    - Connection pooling для повторного использования соединений
    - Rate limiting для предотвращения блокировки
    - Настраиваемые retry и таймауты
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        rate_limit_requests: int = 100,
        rate_limit_window: float = 60.0
    ):
        """
        Args:
            base_url: Базовый URL API
            timeout: Таймаут запросов в секундах
            max_connections: Максимум одновременных соединений
            max_keepalive_connections: Максимум keep-alive соединений
            rate_limit_requests: Максимум запросов в окне
            rate_limit_window: Размер окна rate limit (секунды)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self._sync_client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

        # Rate limiter
        self.rate_limiter = RateLimiter(rate_limit_requests, rate_limit_window)

        # Настройки connection pooling
        self.limits = httpx.Limits(
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections
        )

    @property
    def sync_client(self) -> httpx.Client:
        """Ленивая инициализация синхронного клиента с connection pooling"""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                limits=self.limits,
                follow_redirects=True
            )
        return self._sync_client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Ленивая инициализация асинхронного клиента с connection pooling"""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                limits=self.limits,
                follow_redirects=True
            )
        return self._async_client

    def close(self):
        """Закрыть соединения корректно"""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
        if self._async_client:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._async_client.aclose())
                else:
                    loop.run_until_complete(self._async_client.aclose())
            except RuntimeError:
                asyncio.run(self._async_client.aclose())
            finally:
                self._async_client = None

    async def aclose(self):
        """Асинхронно закрыть соединения"""
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.aclose()

    def __del__(self):
        """Убедимся, что соединения закрыты при удалении объекта"""
        try:
            self.close()
        except:
            pass