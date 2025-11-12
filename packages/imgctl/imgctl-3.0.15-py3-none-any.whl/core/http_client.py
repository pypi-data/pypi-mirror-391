"""
HTTP клиент с централизованным кэшированием

Обеспечивает единую точку для всех HTTP запросов с автоматическим кэшированием
на основе URL и правил кэширования.
"""

import json
from typing import Dict, Optional, Any

import requests

from .cache_manager import CacheManager

# Импорт для callback прогресса
try:
    from .progress import ProgressCallback, NullProgressCallback
except ImportError:
    # Fallback если progress модуль еще не создан
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from .progress import ProgressCallback, NullProgressCallback
    else:
        ProgressCallback = Any


        # Создаем простой fallback класс
        class _NullProgressCallbackFallback:
            def on_request_start(self, description: str): pass

            def on_request_end(self): pass


        NullProgressCallback = _NullProgressCallbackFallback

# Импортируем verbose_print для единого verbose режима
try:
    from utils.verbose import verbose_print
except ImportError:
    # Fallback для случаев когда utils недоступен
    def verbose_print(msg: str):
        pass


class HTTPClient:
    """HTTP клиент с централизованным кэшированием"""

    def __init__(
            self,
            base_url: str,
            cache_manager: Optional[CacheManager] = None,
            verbose: bool = False,
    ):
        """
        Инициализация HTTP клиента

        Args:
            base_url: Базовый URL API
            cache_manager: Менеджер кэша (если None, кэширование отключено)
            verbose: Параметр игнорируется, оставлен для совместимости
        """
        self.base_url = base_url.rstrip("/")
        self.cache = cache_manager
        self.session = requests.Session()

        # Настройки сессии
        self.session.headers.update(
            {
                "User-Agent": "imgctl/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def get(
            self,
            endpoint: str,
            params: Optional[Dict] = None,
            no_cache: bool = False,
            ttl: Optional[int] = None,
            progress: Optional[ProgressCallback] = None,
            **kwargs,
    ) -> requests.Response:
        """
        Выполняет GET запрос с кэшированием

        Args:
            endpoint: Эндпоинт API
            params: Параметры запроса
            no_cache: Не использовать кэш
            ttl: Время жизни кэша в секундах (переопределяет правило)
            progress: Callback для отображения прогресса (вызывается только при реальных запросах)
            **kwargs: Дополнительные параметры для requests

        Returns:
            Response объект
        """
        return self._make_request(
            "GET", endpoint, params=params, no_cache=no_cache, ttl=ttl, progress=progress, **kwargs
        )

    def post(
            self, endpoint: str, data: Optional[Dict] = None, **kwargs
    ) -> requests.Response:
        """
        Выполняет POST запрос

        Args:
            endpoint: Эндпоинт API
            data: Данные для отправки
            **kwargs: Дополнительные параметры для requests

        Returns:
            Response объект
        """
        return self._make_request("POST", endpoint, json=data, **kwargs)

    def put(
            self, endpoint: str, data: Optional[Dict] = None, **kwargs
    ) -> requests.Response:
        """
        Выполняет PUT запрос

        Args:
            endpoint: Эндпоинт API
            data: Данные для отправки
            **kwargs: Дополнительные параметры для requests

        Returns:
            Response объект
        """
        return self._make_request("PUT", endpoint, json=data, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Выполняет DELETE запрос

        Args:
            endpoint: Эндпоинт API
            **kwargs: Дополнительные параметры для requests

        Returns:
            Response объект
        """
        return self._make_request("DELETE", endpoint, **kwargs)

    def _make_request(
            self,
            method: str,
            endpoint: str,
            no_cache: bool = False,
            ttl: Optional[int] = None,
            progress: Optional[ProgressCallback] = None,
            **kwargs,
    ) -> requests.Response:
        """
        Выполняет HTTP запрос с централизованным кэшированием

        Args:
            method: HTTP метод
            endpoint: Эндпоинт API
            no_cache: Не использовать кэш
            ttl: Время жизни кэша в секундах (переопределяет правило)
            progress: Callback для отображения прогресса (вызывается только при реальных запросах)
            **kwargs: Дополнительные параметры для requests
        """
        url = f"{self.base_url}{endpoint}"

        # Инициализируем callback если не передан
        if progress is None:
            progress = NullProgressCallback()

        # Для GET запросов проверяем кэш (если не отключен)
        if method.upper() == "GET" and not no_cache and self.cache:
            try:
                params = kwargs.get("params")
                # Проверяем кеш - логика бесконечного TTL обрабатывается в cache_manager
                cached_data = self.cache.get_cached(url, params)

                if cached_data:
                    data, etag = cached_data

                    # Логируем использование кэша
                    full_url = url
                    if params:
                        params_str = "&".join(
                            f"{k}={v}" for k, v in sorted(params.items())
                        )
                        full_url = f"{url}?{params_str}"

                    verbose_print(f"HTTP GET {full_url} (from cache)")

                    # Callback НЕ вызывается - данные из кеша, запрос мгновенный

                    # Создаем mock response с кэшированными данными
                    response = requests.Response()
                    response.status_code = 200
                    response._content = (
                        json.dumps(data).encode()
                        if isinstance(data, (dict, list))
                        else str(data).encode()
                    )
                    response.headers = {
                        "Content-Type": "application/json",
                        "ETag": etag,
                    }
                    return response
            except Exception:
                pass  # Игнорируем ошибки кэширования

        # Данные не в кеше - будет реальный запрос, вызываем callback
        try:
            # Формируем описание для прогресса
            # Для /deployments/tags используем информацию из параметров
            if endpoint == "/deployments/tags" and kwargs.get("params"):
                params = kwargs.get("params")
                repository = params.get("repository", "")
                image = params.get("image", "")
                # Убираем двоеточие из начала image если есть
                display_image = image.lstrip(":")
                # Убираем __ из конца если есть
                display_image = display_image.rstrip("__")
                description = f"Получение актуального тега для {repository}/{display_image}"
            else:
                description = f"Запрос {method.upper()} {endpoint}"
            progress.on_request_start(description)

            try:
                # Выполняем реальный запрос
                response = self.session.request(method, url, **kwargs)
            finally:
                # Всегда вызываем on_request_end, даже при ошибке
                progress.on_request_end()

            # Для успешных GET запросов сохраняем в кэш
            # no_cache влияет только на чтение из кеша, но не на запись
            if method.upper() == "GET" and self.cache and response.status_code == 200:
                try:
                    data = (
                        response.json()
                        if response.headers.get("Content-Type", "").startswith(
                            "application/json"
                        )
                        else response.text
                    )
                    etag = response.headers.get("ETag", "no-etag")

                    # Логируем сохранение в кэш
                    full_url = url
                    if kwargs.get("params"):
                        params_str = "&".join(
                            f"{k}={v}" for k, v in sorted(kwargs["params"].items())
                        )
                        full_url = f"{url}?{params_str}"
                    verbose_print(f"HTTP GET {full_url} (saved to cache)")

                    # Сохраняем в кэш с централизованными правилами
                    params = kwargs.get("params")
                    self.cache.set_cached(url, params, etag, data, ttl)
                except Exception:
                    pass  # Игнорируем ошибки кэширования

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            raise Exception(f"Ошибка HTTP запроса: {e}")

    def invalidate_cache(self, endpoint: str, params: Optional[Dict] = None) -> None:
        """
        Инвалидирует кэш для конкретного эндпоинта

        Args:
            endpoint: Эндпоинт API
            params: Параметры запроса
        """
        if self.cache:
            url = f"{self.base_url}{endpoint}"
            self.cache.invalidate(url, params)

    def invalidate_cache_pattern(self, pattern: str) -> None:
        """
        Инвалидирует кэш по паттерну

        Args:
            pattern: Паттерн для поиска в URL
        """
        if self.cache:
            self.cache.invalidate_pattern(pattern)

    def clear_cache(self) -> None:
        """Очищает весь кэш"""
        if self.cache:
            self.cache.clear()
