"""
API клиент для работы с «Imagenarium»
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

import requests
from requests.auth import HTTPBasicAuth

from .cache_manager import CacheManager
from .config import Config
from .http_client import HTTPClient

# Импорт для callback прогресса
try:
    from .progress import ProgressCallback, NullProgressCallback
except ImportError:
    ProgressCallback = Any
    NullProgressCallback = None

# Импортируем verbose_print для единого verbose режима
try:
    from utils.verbose import verbose_print
except ImportError:
    # Fallback для случаев когда utils недоступен
    def verbose_print(msg: str):
        pass


class ImagenariumAPIError(Exception):
    """Исключение для ошибок API"""

    pass


class ImagenariumAPIClient:
    """Клиент для работы с API «Imagenarium»"""

    def __init__(
            self, config: Config, enable_cache: bool = True, verbose: bool = False, async_mode: bool = True,
            server_name: Optional[str] = None
    ):
        self.config = config
        self._authenticated = False
        self.async_mode = async_mode
        # Имя сервера для применения сервер-специфичных настроек TTL
        self.server_name = server_name

        # Инициализация кэша с именем сервера для разделения кешей
        if enable_cache:
            # Определяем имя сервера для кеша
            cache_server_name = self._get_cache_server_name()
            self.cache = CacheManager(server_name=cache_server_name)
        else:
            self.cache = None

        # Создаем HTTP клиент
        self.http_client = HTTPClient(config.server, self.cache, verbose)
        self.session = self.http_client.session  # Для совместимости
        self.verbose = verbose

        # Базовый URL
        self.base_url = config.server.rstrip("/")

        # Настройка SSL
        self.session.verify = config.verify_ssl

        # Настройка таймаута
        self.session.timeout = config.timeout

        # Настройка заголовков для оптимизации производительности
        self.session.headers.update(
            {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "ru,en;q=0.9,en-US;q=0.8",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
                "X-Requested-With": "XMLHttpRequest",
            }
        )

        # Загружаем кэшированные cookies если есть
        self._load_cached_cookies()

        # Авторизация через cookie только если нет кэшированных cookies
        if config.username and config.password and not self._authenticated:
            self._authenticate()

        # Фоновый апдейтер кеша для /deployments/list
        import threading
        self._bg_thread = None
        self._bg_stop = threading.Event()
        if self.async_mode:
            # В async режиме устанавливаем максимальный TTL для /deployments/list
            # чтобы данные всегда считались свежими из кеша
            if self.cache:
                # Устанавливаем очень большой TTL (год) для /deployments/list
                # чтобы кеш не считался устаревшим
                # Не сохраняем в конфиг, только для текущего экземпляра
                max_ttl = 86400 * 365  # 1 год
                # Временно переопределяем правило только для этого экземпляра
                # Не сохраняем в конфиг, чтобы не влиять на глобальные настройки
                old_ttl = self.cache._cache_rules.get("/deployments/list", {}).get("ttl", 5)
                self.cache._cache_rules["/deployments/list"] = {
                    "ttl": max_ttl,
                    "strategy": "url",
                    "description": "Список развертываний (async режим)",
                    "_async_override": True,  # Флаг для восстановления
                    "_old_ttl": old_ttl,
                }
                # Если есть server_name, также сохраняем в конфиг для персистентности
                if self.server_name:
                    self.cache.set_server_ttl(self.server_name, "/deployments/list", max_ttl)
            # Запускаем фоновый апдейтер сразу (он сделает первую загрузку в фоне)
            self._start_background_updater()

            # Прогреваем кеш в фоне, не блокируя инициализацию
            def _warmup_cache():
                try:
                    self.get_components(no_cache=False)
                except Exception:
                    pass  # Игнорируем ошибки при первой загрузке

            threading.Thread(target=_warmup_cache, name="imgctl_cache_warmup", daemon=True).start()

    def _start_background_updater(self):
        import threading

        if self._bg_thread and self._bg_thread.is_alive():
            return

        def _worker():
            while not self._bg_stop.wait(timeout=5):
                try:
                    # Фоновый поток всегда делает сетевой запрос для обновления кеша
                    # Используем no_cache=True чтобы игнорировать кеш при чтении, но сохранить результат
                    response = self.http_client.get("/deployments/list", no_cache=True)
                    data = response.json()
                    # Данные автоматически сохраняются в кеш в http_client
                except Exception:
                    pass

        self._bg_thread = threading.Thread(target=_worker, name="imgctl_cache_updater", daemon=True)
        self._bg_thread.start()

    def stop_background_updater(self):
        if self._bg_thread and self._bg_thread.is_alive():
            self._bg_stop.set()

    def set_verbose(self, verbose: bool):
        """Обновляет режим verbose для HTTP клиента"""
        self.verbose = verbose
        self.http_client.verbose = verbose

    def _authenticate(self):
        """Авторизация через cookie для получения сессии"""
        try:
            # Правильный способ авторизации - запрос к главной странице с Basic Auth
            # Это установит cookie сессии
            login_url = f"{self.base_url}/"

            # Устанавливаем правильные заголовки для авторизации
            auth_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "ru",
                "Cache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            }

            auth_response = self.session.get(
                login_url,
                auth=HTTPBasicAuth(self.config.username, self.config.password),
                headers=auth_headers,
                timeout=self.config.timeout,
            )

            if auth_response.status_code == 200:
                self._authenticated = True

                # Добавляем Basic Auth в заголовок для всех запросов
                import base64

                credentials = f"{self.config.username}:{self.config.password}"
                encoded_credentials = base64.b64encode(credentials.encode()).decode()
                self.session.headers.update(
                    {"Authorization": f"Basic {encoded_credentials}"}
                )

                # Добавляем Google Analytics cookies для ускорения (как в браузере)
                import time

                timestamp = int(time.time())
                self.session.cookies.update(
                    {
                        "_ga": f"GA1.1.{timestamp}.{timestamp}",
                        "_ga_0C4M1PWYZ7": f"GS2.1.s{timestamp}$o3$g0$t{timestamp}$j60$l0$h0",
                        "_ga_T11SF3WXX2": f"GS2.1.s{timestamp}$o3$g0$t{timestamp}$j60$l0$h0",
                        "_ga_K2SPJK2C73": f"GS2.1.s{timestamp}$o3$g0$t{timestamp}$j60$l0$h0",
                    }
                )

                # Сохраняем cookies в кэш для повторного использования
                self._save_cached_cookies()

                # Для максимального ускорения можно использовать готовый imgsessionid из браузера
                # Раскомментируйте и замените на актуальный imgsessionid из браузера:
                # self.session.cookies.update({'imgsessionid': '75X_OQjTeJPmfCLmg4jWOcqGqfL6nhlCQ5nEUla5'})
            else:
                raise ImagenariumAPIError(
                    f"Ошибка авторизации: {auth_response.status_code}"
                )

        except Exception as e:
            raise ImagenariumAPIError(f"Ошибка авторизации через cookie: {e}")

    def _get_cache_dir(self) -> Path:
        """Получает директорию кэша в соответствии с канонами ОС"""
        import os

        if os.name == "nt":  # Windows
            cache_dir = Path(os.environ.get("LOCALAPPDATA", "")) / "imgctl" / "cache"
        else:  # Unix-like (Linux, macOS)
            cache_dir = Path.home() / ".cache" / "imgctl"

        # Убеждаемся, что директория существует с безопасными правами
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Устанавливаем безопасные права доступа (только для владельца)
        import stat

        if os.name != "nt":  # Не Windows
            # 0o700 = rwx------ (только владелец может читать/писать/выполнять)
            cache_dir.chmod(stat.S_IRWXU)

        return cache_dir

    def _load_cached_cookies(self):
        """Загружает кэшированные cookies из файла"""
        try:
            import json
            from pathlib import Path

            # Путь к файлу с кэшированными cookies (канонический для ОС)
            cache_dir = self._get_cache_dir()
            cache_dir.mkdir(parents=True, exist_ok=True)
            cookies_file = cache_dir / "cookies.json"

            if cookies_file.exists():
                with open(cookies_file, "r") as f:
                    cached_data = json.load(f)

                # Проверяем, что cookies не устарели (например, не старше 30 минут)
                import time

                if time.time() - cached_data.get("timestamp", 0) < 1800:  # 30 минут
                    cookies = cached_data.get("cookies", {})
                    if cookies:
                        self.session.cookies.update(cookies)
                        self._authenticated = True

                        # Устанавливаем Basic Auth заголовок (как при авторизации)
                        import base64

                        credentials = f"{self.config.username}:{self.config.password}"
                        encoded_credentials = base64.b64encode(
                            credentials.encode()
                        ).decode()
                        self.session.headers.update(
                            {"Authorization": f"Basic {encoded_credentials}"}
                        )

                        # print(f"[DEBUG] Загружены кэшированные cookies: {list(cookies.keys())}")
                        return True

            return False
        except Exception as e:
            print(f"[DEBUG] Ошибка загрузки кэшированных cookies: {e}")
            return False

    def _save_cached_cookies(self):
        """Сохраняет текущие cookies в кэш с безопасными правами доступа"""
        try:
            import json
            import tempfile
            import stat
            import shutil
            import time
            from pathlib import Path

            # Путь к файлу с кэшированными cookies (канонический для ОС)
            cache_dir = self._get_cache_dir()
            cookies_file = cache_dir / "cookies.json"

            # Сохраняем cookies с временной меткой
            cached_data = {
                "timestamp": time.time(),
                "cookies": dict(self.session.cookies),
            }

            # Создаем временный файл для атомарной записи
            with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=cache_dir,
                    delete=False,
                    prefix=".cookies_",
                    suffix=".tmp",
            ) as temp_file:
                json.dump(cached_data, temp_file, indent=2, ensure_ascii=False)
                temp_path = temp_file.name

            # Устанавливаем безопасные права доступа
            import os

            if os.name != "nt":  # Не Windows
                # 0o600 = rw------- (только владелец может читать/писать)
                os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)

            # Атомарно перемещаем временный файл в целевой
            shutil.move(temp_path, cookies_file)

            # print(f"[DEBUG] Сохранены cookies в кэш: {list(cached_data['cookies'].keys())}")
        except Exception as e:
            print(f"[DEBUG] Ошибка сохранения cookies в кэш: {e}")

    def _clear_cached_cookies(self):
        """Очищает кэшированные cookies"""
        try:
            from pathlib import Path

            # Путь к файлу с кэшированными cookies (канонический для ОС)
            cache_dir = self._get_cache_dir()
            cookies_file = cache_dir / "cookies.json"

            if cookies_file.exists():
                cookies_file.unlink()
                # print("[DEBUG] Кэшированные cookies очищены")
        except Exception as e:
            print(f"[DEBUG] Ошибка очистки кэшированных cookies: {e}")

    def _ensure_authenticated(self):
        """Проверяет и при необходимости переавторизуется"""
        if not self._authenticated:
            self._authenticate()

    def get_session_info(self) -> Dict[str, Any]:
        """Возвращает информацию о текущей сессии"""
        return {
            "authenticated": self._authenticated,
            "cookies": dict(self.session.cookies),
            "has_session_cookie": "imgsessionid" in str(self.session.cookies),
            "session_id": self.session.cookies.get("imgsessionid", "не установлен"),
        }

    def _make_request(
            self,
            method: str,
            endpoint: str,
            use_cache: bool = True,
            ttl: Optional[int] = None,
            **kwargs,
    ) -> requests.Response:
        """
        Выполняет HTTP запрос к API с поддержкой кэширования и cookie

        Args:
            method: HTTP метод
            endpoint: Эндпоинт API
            use_cache: Использовать ли кэш для GET запросов
            ttl: Время жизни кэша в секундах (переопределяет автоматический выбор)
            **kwargs: Дополнительные параметры для requests
        """
        # Убеждаемся, что мы авторизованы (только если не авторизованы)
        if not self._authenticated:
            self._ensure_authenticated()

        url = f"{self.base_url}{endpoint}"

        # Определяем, нужно ли использовать кеш для этого URL
        use_cache_for_url = use_cache and self.cache
        if use_cache_for_url and method.upper() == "GET":
            # Получаем имя сервера из base_url
            server_name = self._get_server_name()
            # Проверяем, есть ли правило кеширования для этого URL
            rule = self.cache._get_cache_rule(url, server_name)
            use_cache_for_url = rule["ttl"] > 0  # Используем кеш только если TTL > 0
        elif method.upper() != "GET":
            use_cache_for_url = False  # Для не-GET запросов кеш не используется

        # Для GET запросов проверяем кэш (только если TTL > 0)
        if method.upper() == "GET" and use_cache_for_url:
            cached_data = self.cache.get(url, method)
            if cached_data:
                data, etag = cached_data
                # Если данные в кеше еще не истекли, возвращаем их напрямую
                # (не полагаемся на ETag, так как сервер его не поддерживает должным образом)
                mock_response = requests.Response()
                mock_response.status_code = 200
                mock_response._content = (
                    json.dumps(data).encode()
                    if isinstance(data, (dict, list))
                    else str(data).encode()
                )
                mock_response.headers["Content-Type"] = "application/json"
                return mock_response

        try:
            # Добавляем ETag для условных запросов (только если используем кеш)
            if method.upper() == "GET" and use_cache_for_url:
                cached_data = self.cache.get(url, method)
                if cached_data:
                    data, etag = cached_data
                    if etag != "no-etag":
                        kwargs.setdefault("headers", {}).update({"If-None-Match": etag})

            # Verbose вывод
            if self.verbose:
                # Формируем полный URL с параметрами для отображения
                full_url = url
                if "params" in kwargs and kwargs["params"]:
                    param_str = "&".join(
                        [f"{k}={v}" for k, v in kwargs["params"].items()]
                    )
                    full_url = f"{url}?{param_str}"

                # Определяем статус кеширования
                if method.upper() == "GET" and use_cache:
                    server_name = self._get_server_name()
                    rule = self.cache._get_cache_rule(url, server_name)
                    if rule["ttl"] == 0:
                        cache_status = f"ttl={rule['ttl']}sec"
                    else:
                        cache_status = "no_cache=False"
                elif not use_cache:
                    cache_status = "no_cache=True"
                else:
                    cache_status = "no_cache=False"

                print(f"HTTP {method} {full_url} ({cache_status})")

            response = self.session.request(method, url, **kwargs)

            # Обрабатываем 304 Not Modified
            if response.status_code == 304 and use_cache and self.cache:
                cached_data = self.cache.get(url, method)
                if cached_data:
                    data, etag = cached_data
                    mock_response = requests.Response()
                    mock_response.status_code = 200
                    mock_response._content = (
                        json.dumps(data).encode()
                        if isinstance(data, (dict, list))
                        else str(data).encode()
                    )
                    mock_response.headers["Content-Type"] = "application/json"
                    return mock_response

            # Сохраняем в кэш для будущих запросов (только если TTL > 0)
            if (
                    method.upper() == "GET"
                    and use_cache_for_url
                    and response.status_code == 200
            ):
                try:
                    data = (
                        response.json()
                        if response.headers.get("Content-Type", "").startswith(
                            "application/json"
                        )
                        else response.text
                    )
                    etag = response.headers.get("ETag", "no-etag")

                    # Используем уже определенный TTL
                    cache_ttl = ttl

                    self.cache.set(url, etag, data, method, ttl=cache_ttl)
                except Exception:
                    pass  # Игнорируем ошибки кэширования

            # Обрабатываем ошибки авторизации - переавторизуемся
            if response.status_code in [401, 403]:
                # print(f"[DEBUG] Получена ошибка авторизации {response.status_code}, переавторизуемся...")
                # Очищаем кэшированные cookies
                self._clear_cached_cookies()
                # Переавторизуемся
                self._authenticated = False
                self._authenticate()
                # Повторяем запрос
                response = self.session.request(method, url, **kwargs)

                # Кэшируем результат повторного запроса (только если TTL > 0)
                if (
                        method.upper() == "GET"
                        and use_cache_for_url
                        and response.status_code == 200
                ):
                    try:
                        data = (
                            response.json()
                            if response.headers.get("Content-Type", "").startswith(
                                "application/json"
                            )
                            else response.text
                        )
                        etag = response.headers.get("ETag", "no-etag")

                        # Сохраняем в кэш (TTL определяется в CacheManager)
                        self.cache.set(url, etag, data, method, ttl=ttl)
                    except Exception:
                        pass  # Игнорируем ошибки кэширования

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            raise ImagenariumAPIError(f"Ошибка API запроса: {e}")

    def _get_server_name(self) -> str:
        """Получает имя сервера для сервер-специфичных настроек"""
        # Используем явно переданное имя сервера, если оно есть
        if self.server_name:
            return self.server_name

        # Fallback: получаем из base_url
        from urllib.parse import urlparse
        parsed = urlparse(self.base_url)
        return parsed.hostname or parsed.netloc

    def _get_cache_server_name(self) -> Optional[str]:
        """Получает имя сервера для кеша (для создания подкаталога)"""
        from core.services.servers_service import get_server_name_from_config_or_url

        # Используем переданное имя сервера, если оно есть
        if self.server_name:
            # Проверяем, не является ли это URL
            if self.server_name.startswith(("http://", "https://")):
                # Это URL - пытаемся найти в конфигурации или используем hostname:port
                return get_server_name_from_config_or_url(server=self.server_name)
            else:
                # Это имя сервера
                return self.server_name

        # Если имя сервера не передано, пытаемся определить из URL
        return get_server_name_from_config_or_url(server_url=self.base_url)

    def get_version(self, no_cache: bool = False) -> str:
        """Получает версию «Imagenarium»"""
        response = self._make_request("GET", "/api/v3/version", use_cache=not no_cache)
        return response.text

    def get_nodes(self, no_cache: bool = False) -> List[Dict[str, Any]]:
        """Получает список нод"""
        response = self._make_request("GET", "/api/v3/nodes", use_cache=not no_cache)
        return response.json()

    def update_node(self, node_id: str, node_info: Dict[str, Any]) -> None:
        """Обновляет информацию о ноде"""
        self._make_request("POST", f"/api/v3/nodes/{node_id}", json=node_info)

    def get_config(self) -> Dict[str, Any]:
        """Получает конфигурацию кластера"""
        response = self._make_request("GET", "/api/v3/config")
        return response.json()

    def get_console_config(self, no_cache: bool = False) -> Dict[str, Any]:
        """Получает конфигурацию консоли (название и цвет)"""
        response = self._make_request(
            "GET", "/api/v3/config", use_cache=not no_cache, ttl=86400
        )  # TTL 24 часа
        return response.json()

    def save_config(self, config: Dict[str, Any]) -> None:
        """Сохраняет конфигурацию кластера"""
        self._make_request("POST", "/api/v3/config", json=config)

    def get_registries(
            self,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> List[Dict[str, Any]]:
        """Получает список реестров"""
        response = self.http_client.get(
            "/api/v3/registries",
            no_cache=no_cache,
            progress=progress,
        )
        return response.json()

    def add_registry(self, registry_info: Dict[str, Any]) -> None:
        """Добавляет новый реестр"""
        self._make_request("POST", "/api/v3/registries", json=registry_info)
        # Автоматически инвалидируем кеш реестров
        self.invalidate_registries_cache()

    def delete_registry(self, registry_id: str) -> None:
        """Удаляет реестр"""
        self._make_request("DELETE", f"/api/v3/registries/{registry_id}")
        # Автоматически инвалидируем кеш реестров
        self.invalidate_registries_cache()

    def get_repositories(
            self,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> List[Dict[str, Any]]:
        """Получает список репозиториев"""
        response = self.http_client.get(
            "/api/v3/repositories",
            no_cache=no_cache,
            progress=progress,
        )
        return response.json()

    def add_repository(self, repository_info: Dict[str, Any]) -> None:
        """Добавляет новый репозиторий"""
        self._make_request("POST", "/api/v3/repositories", json=repository_info)
        # Автоматически инвалидируем кеш репозиториев
        self.invalidate_repositories_cache()

    def delete_repository(self, repository_id: str) -> None:
        """Удаляет репозиторий"""
        self._make_request("DELETE", f"/api/v3/repositories/{repository_id}")
        # Автоматически инвалидируем кеш репозиториев
        self.invalidate_repositories_cache()

    def deploy_stack(
            self,
            namespace: str,
            stack_id: str,
            version: str,
            repository: str,
            git_ref: str,
            params: Optional[Dict[str, str]] = None,
    ) -> None:
        """Деплоит стек в namespace"""
        query_params = {"repository": repository, "gitRef": git_ref}
        self._make_request(
            "POST",
            f"/api/v3/deploy/stack/{namespace}/{stack_id}/{version}",
            params=query_params,
            json=params or {},
        )
        # Автоматически инвалидируем кеш компонентов и стеков
        self.invalidate_components_cache()
        self.invalidate_stacks_cache()

    def undeploy_stack(
            self, namespace: str, stack_id: str, version: str
    ) -> Dict[str, Any]:
        """Андеплоит стек из namespace"""
        response = self._make_request(
            "POST", f"/api/v3/undeploy/stack/{namespace}/{stack_id}/{version}"
        )
        # Автоматически инвалидируем кеш компонентов и стеков
        self.invalidate_components_cache()
        self.invalidate_stacks_cache()
        return response.json()

    def deploy_group(
            self,
            namespace: str,
            group_id: str,
            version: str,
            repository: str,
            git_ref: str,
            params: Optional[Dict[str, Dict[str, str]]] = None,
    ) -> None:
        """Деплоит группу в namespace"""
        query_params = {"repository": repository, "gitRef": git_ref}
        self._make_request(
            "POST",
            f"/api/v3/deploy/group/{namespace}/{group_id}/{version}",
            params=query_params,
            json=params or {},
        )

    def undeploy_namespace(self, namespace: str) -> None:
        """Андеплоит весь namespace"""
        self._make_request("POST", f"/api/v3/undeploy/namespace/{namespace}")

    def get_components(
            self,
            namespace: Optional[str] = None,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получает список компонентов

        Args:
            namespace: Фильтр по namespace (если None, возвращает все)
            no_cache: Не использовать кеш
            progress: Callback для отображения прогресса (вызывается только при реальных запросах)

        Returns:
            Список компонентов
        """
        response = self.http_client.get("/deployments/list", no_cache=no_cache, progress=progress)
        data = response.json()

        if namespace:
            # Фильтруем на клиенте
            return [
                item
                for item in data
                if item.get("namespace", "").lower() == namespace.lower()
            ]
        else:
            return data

    def update_component(
            self, name: str, image: str, namespace: str = None, stack: str = None, component_data: dict = None
    ) -> None:
        """Обновляет образ компонента"""
        query_params = {"image": image, "runApp": "true"}

        # Если namespace и stack не указаны, пытаемся извлечь их из имени компонента
        if not namespace or not stack:
            # Предполагаем формат: stack-namespace или stack_namespace
            if "-" in name:
                parts = name.split("-")
                if len(parts) >= 3:
                    # Для oms-api-v3-suzlet-suz5:
                    # parts = ['oms', 'api', 'v3', 'suzlet', 'suz5']
                    # stack = 'oms-api-v3', namespace = 'suzlet-suz5'
                    # Ищем последние 2 части как namespace
                    namespace = "-".join(parts[-2:])  # suzlet-suz5
                    stack = "-".join(parts[:-2])  # oms-api-v3
                elif len(parts) == 2:
                    # Простой случай: stack-namespace
                    stack = parts[0]
                    namespace = parts[1]

        # Определяем тип компонента для выбора правильного endpoint
        component_type = None
        if component_data:
            component_type = component_data.get("@c")
        
        # Если тип компонента не найден, получаем из API
        if not component_type:
            comp_details = self.get_component_details(name, no_cache=False)
            if comp_details:
                component_type = comp_details.get("@c")

        if namespace and stack:
            # Выбираем endpoint на основе типа компонента
            if component_type == ".DeployedService":
                endpoint = f"/deployments/update/service/{namespace}/{stack}/{name}"
            else:
                endpoint = f"/deployments/update/runner/{namespace}/{stack}/{name}"
        else:
            # Fallback к старому API если не удалось определить namespace и stack
            endpoint = f"/api/v3/component/update/{name}"

        full_url = f"{self.base_url}{endpoint}?{'&'.join(f'{k}={v}' for k, v in query_params.items())}"

        # DEBUG вывод при verbose режиме
        verbose_print(f"Update component: {name}")
        verbose_print(f"Endpoint: {endpoint}")
        verbose_print(f"Full URL: {full_url}")
        if component_type:
            verbose_print(f"Component type: {component_type}")

        self._make_request("GET", endpoint, params=query_params)
        # Автоматически инвалидируем кеш компонентов
        self.invalidate_components_cache()

    def stop_component(self, name: str) -> None:
        """Останавливает компонент"""
        self._make_request("POST", f"/api/v3/component/stop/{name}")
        # В shell режиме кэш обновляется фоновым потоком, не сбрасываем
        if os.environ.get("IMGCTL_SHELL_MODE") != "1":
            self.invalidate_components_cache()

    def start_component(self, name: str) -> None:
        """Запускает компонент"""
        self._make_request("POST", f"/api/v3/component/start/{name}")
        # В shell режиме кэш обновляется фоновым потоком, не сбрасываем
        if os.environ.get("IMGCTL_SHELL_MODE") != "1":
            self.invalidate_components_cache()

    def get_template(
            self,
            repo_name: str,
            stack_id: str,
            version: str,
            git_ref: str,
            progress: Optional[ProgressCallback] = None,
    ) -> str:
        """Получает шаблон деплоя"""
        query_params = {"gitRef": git_ref}
        response = self.http_client.get(
            f"/api/v3/templates/{repo_name}/{stack_id}/{version}",
            params=query_params,
            progress=progress,
        )
        return response.text

    def diff_template(
            self,
            namespace: str,
            stack_id: str,
            version: str,
            new_git_ref: str,
            progress: Optional[ProgressCallback] = None,
    ) -> Dict[str, Any]:
        """Получает diff шаблонов"""
        query_params = {"newGitRef": new_git_ref}
        response = self.http_client.get(
            f"/api/v3/templates/diff/{namespace}/{stack_id}/{version}",
            params=query_params,
            progress=progress,
        )
        return response.json()

    def get_stacks(self, no_cache: bool = False) -> List[Dict[str, Any]]:
        """Получает список стеков из компонентов"""
        components = self.get_components(no_cache=no_cache)

        # Группируем компоненты по стекам
        stacks = {}
        for component in components:
            stacks_data = component.get("stacks", [])
            if not stacks_data:
                continue

            for stack_data in stacks_data:
                stack_id = stack_data.get("stackId")
                if not stack_id:
                    continue

                namespace = stack_data.get("namespace", "N/A")
                stack_name_with_namespace = f"{stack_id}@{namespace}"

                if stack_name_with_namespace not in stacks:
                    stacks[stack_name_with_namespace] = {
                        "id": stack_id,
                        "name": stack_name_with_namespace,
                        "namespace": namespace,
                        "version": stack_data.get("version", "N/A"),
                        "repository": stack_data.get("repo", "N/A"),
                        "gitRef": stack_data.get("commit", "N/A"),
                        "timestamp": stack_data.get("timestamp", "N/A"),
                        "tag": stack_data.get("tag", None),
                        "parameters": stack_data.get("params", {}),
                        "status": stack_data.get("status", "UNKNOWN"),
                        "components": [],
                    }

                # Добавляем компонент к стеку из данных стека
                stack_components = stack_data.get("components", [])
                for stack_component in stack_components:
                    stacks[stack_name_with_namespace]["components"].append(
                        {
                            "name": stack_component.get("name", "N/A"),
                            "description": f"Компонент {stack_component.get('name', 'N/A')}",
                            "image": stack_component.get("image", "N/A"),
                        }
                    )

        return list(stacks.values())

    def get_stack_details(self, stack_id: str) -> Dict[str, Any]:
        """Получает детальную информацию о стеке"""
        stacks = self.get_stacks()

        # Ищем стек по ID или по имени с namespace
        for stack in stacks:
            if stack.get("id") == stack_id or stack.get("name") == stack_id:
                return stack

        return {}

    def clear_cache(self) -> None:
        """Очищает кэш"""
        self.http_client.clear_cache()

    def invalidate_cache(self, pattern: str) -> None:
        """
        Инвалидирует кэш по паттерну

        Args:
            pattern: Паттерн для поиска URL в кэше
        """
        self.http_client.invalidate_cache_pattern(pattern)

    def invalidate_cache_pattern(self, pattern: str) -> None:
        """Алиас для invalidate_cache"""
        self.invalidate_cache(pattern)

    def invalidate_deployment_tags_cache(self, repository: str, image: str) -> None:
        """
        Инвалидирует кеш тегов развертываний для конкретного репозитория и образа

        Args:
            repository: Имя репозитория
            image: Образ для поиска
        """
        if self.cache:
            self.cache.invalidate_deployment_tags(repository, image)

    def invalidate_deployment_tags_cache_pattern(self, pattern: str) -> None:
        """
        Инвалидирует кеш тегов развертываний по паттерну

        Args:
            pattern: Паттерн для поиска (repository или image)
        """
        if self.cache:
            self.cache.invalidate_deployment_tags_pattern(pattern)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Возвращает статистику кэша"""
        if self.cache:
            return self.cache.get_stats()
        return {}

    def cleanup_cache(self) -> int:
        """
        Очищает истекшие записи из кэша

        Returns:
            Количество удаленных записей
        """
        if self.cache:
            return self.cache.cleanup_expired()
        return 0

    def get_component_details(
            self,
            component_name: str,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Получает детальную информацию о конкретном компоненте

        Args:
            component_name: Имя компонента
            no_cache: Не использовать кеш
            progress: Callback для отображения прогресса (вызывается только при реальных запросах)

        Returns:
            Словарь с детальной информацией о компоненте или None, если не найден
        """
        try:
            # Получаем все компоненты
            components = self.get_components(no_cache=no_cache, progress=progress)

            # Ищем компонент по имени
            for group in components:
                stacks = group.get("stacks", [])
                for stack in stacks:
                    stack_components = stack.get("components", [])
                    for comp in stack_components:
                        comp_name = comp.get("name", "")

                        # Проверяем точное совпадение имени
                        if comp_name == component_name:
                            # Проверяем, есть ли у компонента задачи (это runner компонент)
                            if "tasks" in comp and comp.get("tasks"):
                                # Возвращаем компонент с дополнительной информацией о стеке и namespace
                                result = comp.copy()
                                namespace = group.get("namespace")
                                stack_id = stack.get("stackId")
                                result["namespace"] = namespace
                                result["stack_id"] = f"{stack_id}@{namespace}"
                                result["stack_version"] = stack.get("version")
                                result["stack_status"] = stack.get("status")
                                result["stack_repo"] = stack.get("repo")
                                result["stack_branch"] = stack.get("branch")
                                result["stack_commit"] = stack.get("commit")
                                result["stack_tag"] = stack.get("tag")
                                result["stack_timestamp"] = stack.get("timestamp")
                                return result

            return None
        except Exception:
            return None

    def find_component_id_by_name(
            self,
            component_name: str,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> Optional[str]:
        """
        Находит ID компонента по имени

        Args:
            component_name: Имя компонента
            no_cache: Не использовать кеш
            progress: Callback для отображения прогресса (вызывается только при реальных запросах)

        Returns:
            ID компонента или None, если не найден
        """
        component = self.get_component_details(component_name, no_cache=no_cache, progress=progress)
        return component.get("id") if component else None

    def get_deployment_tags(
            self,
            repository: str,
            image: str,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получает список тегов развертываний для указанного репозитория и образа

        Args:
            repository: Имя репозитория
            image: Полное имя образа с тегом
            no_cache: Не использовать кеш
            progress: Callback для отображения прогресса (вызывается только при реальных запросах)

        Returns:
            Список тегов с информацией о текущем статусе
        """
        query_params = {"repository": repository, "image": image}
        response = self.http_client.get(
            "/deployments/tags", params=query_params, no_cache=no_cache, progress=progress
        )
        return response.json()

    def get_latest_deployment_tag(
            self, repository: str, image: str, no_cache: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Эффективно получает последний (текущий) тег развертывания

        Этот метод оптимизирован для получения только последней записи:
        1. Использует кеширование с TTL 30 секунд
        2. Возвращает только текущий тег (current: true)
        3. Минимизирует передачу данных

        Args:
            repository: Имя репозитория
            image: Полное имя образа с тегом

        Returns:
            Словарь с информацией о последнем теге или None, если не найден
        """
        try:
            # Получаем все теги
            tags = self.get_deployment_tags(repository, image, no_cache)

            # Ищем текущий тег (current: true)
            for tag in tags:
                if tag.get("current", False):
                    return tag

            # Если текущий тег не найден, возвращаем первый (самый новый)
            return tags[0] if tags else None

        except Exception as e:
            raise ImagenariumAPIError(
                f"Ошибка получения последнего тега развертывания: {e}"
            )

    def get_deployment_tags_count(self, repository: str, image: str) -> int:
        """
        Получает количество доступных тегов развертывания

        Args:
            repository: Имя репозитория
            image: Полное имя образа с тегом

        Returns:
            Количество доступных тегов
        """
        try:
            tags = self.get_deployment_tags(repository, image)
            return len(tags)
        except Exception as e:
            raise ImagenariumAPIError(f"Ошибка получения количества тегов: {e}")

    # Семантические методы для инвалидации кеша
    def invalidate_components_cache(self) -> None:
        """Инвалидирует кеш компонентов"""
        self.invalidate_cache("/deployments/list")
        self.invalidate_cache("/api/v3/components")

    def invalidate_stacks_cache(self) -> None:
        """Инвалидирует кеш стеков"""
        self.invalidate_cache("/stacks")
        self.invalidate_cache("/api/v3/stacks")

    def invalidate_nodes_cache(self) -> None:
        """Инвалидирует кеш нод"""
        self.invalidate_cache("/nodes")
        self.invalidate_cache("/api/v3/nodes")

    def invalidate_registries_cache(self) -> None:
        """Инвалидирует кеш реестров"""
        self.invalidate_cache("/registries")
        self.invalidate_cache("/api/v3/registries")

    def invalidate_repositories_cache(self) -> None:
        """Инвалидирует кеш репозиториев"""
        self.invalidate_cache("/repositories")
        self.invalidate_cache("/api/v3/repositories")

    def invalidate_component_cache(self, component_name: str) -> None:
        """Инвалидирует кеш конкретного компонента"""
        self.invalidate_cache(f"component_id:{component_name}")
        self.invalidate_cache("deployments/list")
        self.invalidate_cache("api/v3/components")
        self.invalidate_deployment_tags_cache_pattern("deployment_tags:")

    def invalidate_all_cache(self) -> None:
        """Инвалидирует весь кеш"""
        if self.cache:
            self.cache.clear()
