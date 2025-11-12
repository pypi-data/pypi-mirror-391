"""
Модуль для управления кэшем с поддержкой ETag

Обеспечивает кэширование HTTP ответов с использованием ETag заголовков
для оптимизации повторных запросов.
"""

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any, Tuple


@dataclass
class CacheEntry:
    """Запись в кэше"""

    url: str
    etag: str
    data: Any
    timestamp: datetime
    expires_at: Optional[datetime] = None
    ttl_zero: bool = False  # Флаг для TTL=0 (всегда истекшая)
    ttl_infinite: bool = False  # Флаг для бесконечного TTL (никогда не истекшая)

    def is_expired(self) -> bool:
        """Проверяет, истек ли срок действия кэша"""
        if self.expires_at is None:
            return False
        # Если TTL бесконечный, запись никогда не истекшая
        if self.ttl_infinite:
            return False
        # Если TTL был 0, запись всегда истекшая
        if self.ttl_zero:
            return True
        return datetime.now() > self.expires_at

    def to_dict(self) -> Dict:
        """Преобразует в словарь для сериализации"""
        return {
            "url": self.url,
            "etag": self.etag,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "ttl_zero": self.ttl_zero,
            "ttl_infinite": self.ttl_infinite,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CacheEntry":
        """Создает из словаря"""
        return cls(
            url=data["url"],
            etag=data["etag"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            expires_at=(
                datetime.fromisoformat(data["expires_at"])
                if data.get("expires_at")
                else None
            ),
            ttl_zero=data.get("ttl_zero", False),  # Обратная совместимость
            ttl_infinite=data.get("ttl_infinite", False),  # Обратная совместимость
        )


class CacheManager:
    """Централизованный менеджер кэша с правилами для разных типов URL"""

    def __init__(self, cache_dir: Optional[Path] = None, default_ttl: int = 300, server_name: Optional[str] = None):
        """
        Инициализация менеджера кэша

        Args:
            cache_dir: Директория для хранения кэша
            default_ttl: Время жизни кэша по умолчанию в секундах
            server_name: Имя сервера для создания подкаталога кеша
        """
        if cache_dir is None:
            # Используем стандартную директорию кэша
            if os.name == "nt":  # Windows
                base_cache_dir = (
                        Path(os.environ.get("LOCALAPPDATA", "")) / "imgctl" / "cache"
                )
            else:  # Unix-like
                base_cache_dir = Path.home() / ".cache" / "imgctl"

            # Если указано имя сервера, создаем подкаталог
            if server_name:
                cache_dir = base_cache_dir / server_name
            else:
                cache_dir = base_cache_dir
        else:
            # Если cache_dir передан явно, но есть server_name, добавляем подкаталог
            if server_name:
                cache_dir = cache_dir / server_name

        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.cache_file = cache_dir / "cache.json"
        self.config_file = cache_dir / "cache_config.json"
        self._ensure_cache_dir()
        self._cache: Dict[str, CacheEntry] = self._load_cache()

        # Правила кеширования для разных типов URL
        self._cache_rules = {
            # Всегда обновляется (TTL 0 секунд)
            "/api/v3/nodes": {
                "ttl": 0,  # Всегда обновляется
                "strategy": "url",
                "description": "Список нод",
            },
            "/api/v3/repositories": {
                "ttl": 0,  # Всегда обновляется
                "strategy": "url",
                "description": "Список репозиториев",
            },
            "/api/v3/registries": {
                "ttl": 0,  # Всегда обновляется
                "strategy": "url",
                "description": "Список реестров",
            },
            "/api/v3/version": {
                "ttl": 3600,  # TTL 1 час
                "strategy": "url",
                "description": "Версия системы",
            },
            # Быстрое обновление (TTL 5 секунд)
            "/deployments/list": {
                "ttl": 5,  # 5 секунд
                "strategy": "url",
                "description": "Список развертываний",
            },
            # Медленный API (TTL 30 секунд)
            "/deployments/tags": {
                "ttl": 30,  # 30 секунд
                "strategy": "params",  # Кешируем по параметрам repository + image
                "description": "Теги развертываний",
            },
            # Конфигурация консоли (TTL 24 часа)
            "/api/v3/config": {
                "ttl": 86400,  # 24 часа
                "strategy": "url",
                "description": "Конфигурация консоли",
            },
        }

        # Загружаем пользовательские настройки TTL
        self._load_user_config()

    def _load_user_config(self):
        """Загружает пользовательские настройки TTL из файла конфигурации"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    import json

                    user_config = json.load(f)

                    # Применяем пользовательские настройки (пока глобально)
                    for endpoint, ttl in user_config.get("ttl_overrides", {}).items():
                        if endpoint in self._cache_rules:
                            self._cache_rules[endpoint]["ttl"] = ttl
        except Exception:
            # Игнорируем ошибки загрузки конфигурации
            pass

    def _save_user_config(self):
        """Сохраняет пользовательские настройки TTL в файл конфигурации"""
        try:
            # Собираем только измененные настройки
            ttl_overrides = {}
            default_rules = self._get_default_rules()

            for endpoint, rule in self._cache_rules.items():
                if (
                        endpoint in default_rules
                        and rule["ttl"] != default_rules[endpoint]["ttl"]
                ):
                    ttl_overrides[endpoint] = rule["ttl"]

            config = {"ttl_overrides": ttl_overrides, "version": "1.0"}

            with open(self.config_file, "w", encoding="utf-8") as f:
                import json

                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception:
            # Игнорируем ошибки сохранения конфигурации
            pass

    def _get_default_rules(self):
        """Возвращает правила кеширования по умолчанию"""
        return {
            # Всегда обновляется (TTL 0 секунд)
            "/api/v3/nodes": {
                "ttl": 0,  # Всегда обновляется
                "strategy": "url",
                "description": "Список нод",
            },
            "/api/v3/repositories": {
                "ttl": 0,  # Всегда обновляется
                "strategy": "url",
                "description": "Список репозиториев",
            },
            "/api/v3/registries": {
                "ttl": 0,  # Всегда обновляется
                "strategy": "url",
                "description": "Список реестров",
            },
            "/api/v3/version": {
                "ttl": 3600,  # TTL 1 час
                "strategy": "url",
                "description": "Версия системы",
            },
            # Быстрое обновление (TTL 5 секунд)
            "/deployments/list": {
                "ttl": 5,  # 5 секунд
                "strategy": "url",
                "description": "Список развертываний",
            },
            # Медленный API (TTL 30 секунд)
            "/deployments/tags": {
                "ttl": 30,  # 30 секунд
                "strategy": "params",  # Кешируем по параметрам repository + image
                "description": "Теги развертываний",
            },
            # Конфигурация консоли (TTL 24 часа)
            "/api/v3/config": {
                "ttl": 86400,  # 24 часа
                "strategy": "url",
                "description": "Конфигурация консоли",
            },
        }

    def _ensure_cache_dir(self):
        """Создает директорию кэша если не существует с безопасными правами доступа"""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Устанавливаем безопасные права доступа (только для владельца)
        import stat

        if os.name != "nt":  # Не Windows
            # 0o700 = rwx------ (только владелец может читать/писать/выполнять)
            self.cache_dir.chmod(stat.S_IRWXU)

    def _get_cache_rule(self, url: str, server: str = None) -> Dict[str, Any]:
        """
        Получает правило кеширования для URL

        Args:
            url: URL для которого нужно получить правило
            server: Имя сервера (для сервер-специфичных настроек)

        Returns:
            Словарь с правилами кеширования
        """
        # Извлекаем путь из URL (убираем протокол и хост)
        from urllib.parse import urlparse

        parsed = urlparse(url)
        path = parsed.path

        # Ищем правило по префиксу пути
        for prefix, rule in self._cache_rules.items():
            if path.startswith(prefix):
                # Создаем копию правила для модификации
                rule_copy = rule.copy()

                # Если указан сервер, проверяем сервер-специфичные настройки
                if server:
                    server_ttl = self._get_server_ttl(server, path)
                    if server_ttl is not None:
                        rule_copy["ttl"] = server_ttl

                return rule_copy

        # Возвращаем правило по умолчанию
        default_rule = {
            "ttl": self.default_ttl,
            "strategy": "url",
            "description": "По умолчанию",
        }

        # Если указан сервер, проверяем сервер-специфичные настройки
        if server:
            server_ttl = self._get_server_ttl(server, path)
            if server_ttl is not None:
                default_rule["ttl"] = server_ttl

        return default_rule

    def _get_server_ttl(self, server: str, path: str) -> Optional[int]:
        """Получает TTL для конкретного сервера и пути"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    import json

                    user_config = json.load(f)

                    # Проверяем сервер-специфичные настройки
                    server_config = user_config.get("servers", {}).get(server, {})
                    return server_config.get("ttl_overrides", {}).get(path)
        except Exception:
            pass
        return None

    def set_server_ttl(self, server: str, endpoint: str, ttl: int):
        """Устанавливает TTL для конкретного сервера и эндпоинта"""
        try:
            # Загружаем текущую конфигурацию
            config = {}
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    import json

                    config = json.load(f)

            # Инициализируем структуру для серверов
            if "servers" not in config:
                config["servers"] = {}
            if server not in config["servers"]:
                config["servers"][server] = {"ttl_overrides": {}}
            if "ttl_overrides" not in config["servers"][server]:
                config["servers"][server]["ttl_overrides"] = {}

            # Устанавливаем TTL
            config["servers"][server]["ttl_overrides"][endpoint] = ttl

            # Сохраняем конфигурацию
            with open(self.config_file, "w", encoding="utf-8") as f:
                import json

                json.dump(config, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise Exception(f"Ошибка сохранения настроек сервера: {e}")

    def get_server_ttl_settings(self, server: str = None) -> Dict[str, Any]:
        """Получает настройки TTL для сервера или всех серверов"""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    import json

                    config = json.load(f)

                    if server:
                        return config.get("servers", {}).get(server, {})
                    else:
                        return config.get("servers", {})
        except Exception:
            pass
        return {}

    def _get_cache_key(self, url: str, params: Optional[Dict] = None) -> str:
        """
        Генерирует ключ кеша на основе URL и параметров

        Args:
            url: URL запроса
            params: Параметры запроса

        Returns:
            Ключ для кеша
        """
        rule = self._get_cache_rule(url)

        if rule["strategy"] == "url":
            # Кешируем по полному URL
            return hashlib.md5(url.encode()).hexdigest()
        elif rule["strategy"] == "params" and params:
            # Кешируем по параметрам (для /deployments/tags)
            if "repository" in params and "image" in params:
                # Специальная логика для тегов развертываний
                repo = params["repository"]
                image = params["image"]

                if "__" in image:
                    # Для тегов с __ используем repo + префикс до __
                    tag_prefix = image.split("__")[0] + "__"
                    cache_key_data = f"deployment_tags:{repo}:{tag_prefix}"
                else:
                    # Для простых тегов используем repo + полный image
                    cache_key_data = f"deployment_tags:{repo}:{image}"

                return hashlib.md5(cache_key_data.encode()).hexdigest()
            else:
                # Для других параметров используем URL + параметры
                params_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
                cache_key_data = f"{url}?{params_str}"
                return hashlib.md5(cache_key_data.encode()).hexdigest()
        else:
            # По умолчанию используем URL
            return hashlib.md5(url.encode()).hexdigest()

    def get_cached(
            self, url: str, params: Optional[Dict] = None
    ) -> Optional[Tuple[Any, str]]:
        """
        Получает данные из кеша

        Args:
            url: URL запроса
            params: Параметры запроса

        Returns:
            Tuple (данные, etag) или None если не найдено или истек

        Note:
            Для записей с бесконечным TTL (ttl_infinite=True) данные всегда возвращаются,
            так как они никогда не истекают. Для других записей данные возвращаются только
            если они еще не истекли.
        """
        try:
            key = self._get_cache_key(url, params)
            entry = self._cache.get(key)

            if entry is None:
                return None

            # Для TTL=0 всегда возвращаем None (не используем кеш)
            if entry.ttl_zero:
                return None

            # Если запись истекла, возвращаем None
            if entry.is_expired():
                # Удаляем истекшую запись (но не сохраняем сразу - это можно сделать асинхронно)
                # чтобы не блокировать другие потоки
                try:
                    del self._cache[key]
                except KeyError:
                    pass  # Уже удалено другим потоком
                return None

            # Запись существует и не истекла (включая бесконечный TTL)
            return entry.data, entry.etag
        except Exception:
            return None

    def set_cached(
            self,
            url: str,
            params: Optional[Dict] = None,
            etag: str = "no-etag",
            data: Any = None,
            ttl: Optional[int] = None,
    ) -> None:
        """
        Сохраняет данные в кеш

        Args:
            url: URL запроса
            params: Параметры запроса
            etag: ETag заголовок
            data: Данные для кеширования
            ttl: Время жизни в секундах (переопределяет правило)
        """
        # Получаем правило кеша - для сервер-специфичных настроек нужно передать server_name
        # Но так как server_name может быть недоступен здесь, используем правило без server_name
        # Сервер-специфичные настройки TTL применяются через set_server_ttl в api_client
        rule = self._get_cache_rule(url, server=None)

        if ttl is None:
            ttl = rule["ttl"]

        # Определяем, является ли TTL бесконечным (для async режима)
        # Используем порог в 1 год (31536000 секунд)
        INFINITE_TTL_THRESHOLD = 86400 * 365  # 1 год
        ttl_infinite = ttl >= INFINITE_TTL_THRESHOLD

        # Для бесконечного TTL не устанавливаем expires_at
        expires_at = None if ttl_infinite else (datetime.now() + timedelta(seconds=ttl))

        entry = CacheEntry(
            url=url,
            etag=etag,
            data=data,
            timestamp=datetime.now(),
            expires_at=expires_at,
            ttl_zero=(ttl == 0),  # Устанавливаем флаг для TTL=0
            ttl_infinite=ttl_infinite,  # Устанавливаем флаг для бесконечного TTL
        )

        key = self._get_cache_key(url, params)
        # Атомарно заменяем запись (для Python dict это операция атомарная)
        # Запись сначала добавляется в память, потом сохраняется в файл
        self._cache[key] = entry
        # Сохранение в файл делаем в фоне (не блокируем запись в память)
        # Основной поток может читать из памяти пока файл сохраняется
        try:
            self._save_cache()
        except Exception:
            pass  # Игнорируем ошибки сохранения в файл - данные уже в памяти

    def invalidate(self, url: str, params: Optional[Dict] = None) -> None:
        """
        Удаляет запись из кеша

        Args:
            url: URL запроса
            params: Параметры запроса
        """
        key = self._get_cache_key(url, params)
        if key in self._cache:
            del self._cache[key]
            self._save_cache()

    def invalidate_pattern(self, pattern: str) -> None:
        """
        Удаляет записи по паттерну

        Args:
            pattern: Паттерн для поиска в URL
        """
        keys_to_remove = []
        for key, entry in self._cache.items():
            if pattern in entry.url:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]

        if keys_to_remove:
            self._save_cache()

    def _load_cache(self) -> Dict[str, CacheEntry]:
        """Загружает кэш из файла"""
        if not self.cache_file.exists():
            return {}

        try:
            with open(self.cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                cache = {}
                for key, entry_data in data.items():
                    try:
                        cache[key] = CacheEntry.from_dict(entry_data)
                    except Exception:
                        # Пропускаем поврежденные записи
                        continue
                return cache
        except Exception:
            return {}

    def _save_cache(self):
        """Сохраняет кэш в файл с безопасными правами доступа"""
        try:
            data = {key: entry.to_dict() for key, entry in self._cache.items()}

            # Создаем временный файл для атомарной записи
            import tempfile
            import stat

            with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.cache_dir,
                    delete=False,
                    prefix=".cache_",
                    suffix=".tmp",
            ) as temp_file:
                json.dump(data, temp_file, indent=2, ensure_ascii=False)
                temp_path = temp_file.name

            # Устанавливаем безопасные права доступа
            if os.name != "nt":  # Не Windows
                # 0o600 = rw------- (только владелец может читать/писать)
                os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)

            # Атомарно перемещаем временный файл в целевой
            import shutil

            shutil.move(temp_path, self.cache_file)

        except Exception:
            pass  # Игнорируем ошибки сохранения

    def _get_cache_key(self, url: str, method: str = "GET") -> str:
        """Генерирует ключ кэша для URL и метода"""
        key_data = f"{method}:{url}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def _get_deployment_tags_cache_key(self, repository: str, image: str) -> str:
        """
        Генерирует специальный ключ кэша для тегов развертываний

        Стратегия:
        - Если в image есть __ (например, dev__2025_10_08_14_58-d6e6c8c),
          используем repo + префикс до __ (например, emi + :dev__)
        - Если в image нет __ (например, harbor.crpt.tech/suz/imagenarium/postgresql:12.3),
          используем repo + полный image
        """
        if "__" in image:
            # Извлекаем префикс до __
            tag_prefix = image.split("__")[0] + "__"
            cache_key_data = f"deployment_tags:{repository}:{tag_prefix}"
        else:
            # Используем полный image
            cache_key_data = f"deployment_tags:{repository}:{image}"

        return hashlib.md5(cache_key_data.encode()).hexdigest()

    def get(self, url: str, method: str = "GET") -> Optional[Tuple[Any, str]]:
        """
        Получает данные из кэша

        Args:
            url: URL запроса
            method: HTTP метод

        Returns:
            Tuple (данные, etag) или None если не найдено
        """
        key = self._get_cache_key(url, method)
        entry = self._cache.get(key)

        if entry is None or entry.is_expired():
            if entry and entry.is_expired():
                # Удаляем истекшую запись
                del self._cache[key]
                self._save_cache()
            return None

        return entry.data, entry.etag

    def get_deployment_tags(
            self, repository: str, image: str
    ) -> Optional[Tuple[Any, str]]:
        """
        Получает данные тегов развертываний из кэша с специальной стратегией

        Args:
            repository: Имя репозитория
            image: Образ для поиска

        Returns:
            Tuple (данные, etag) или None если не найдено
        """
        key = self._get_deployment_tags_cache_key(repository, image)
        entry = self._cache.get(key)

        if entry is None or entry.is_expired():
            if entry and entry.is_expired():
                # Удаляем истекшую запись
                del self._cache[key]
                self._save_cache()
            return None

        return entry.data, entry.etag

    def set(
            self,
            url: str,
            etag: str,
            data: Any,
            method: str = "GET",
            ttl: Optional[int] = None,
    ) -> None:
        """
        Сохраняет данные в кэш

        Args:
            url: URL запроса
            etag: ETag заголовок
            data: Данные для кэширования
            method: HTTP метод
            ttl: Время жизни в секундах (по умолчанию default_ttl)
        """
        if ttl is None:
            ttl = self.default_ttl

        expires_at = datetime.now() + timedelta(seconds=ttl)

        entry = CacheEntry(
            url=url,
            etag=etag,
            data=data,
            timestamp=datetime.now(),
            expires_at=expires_at,
        )

        key = self._get_cache_key(url, method)
        self._cache[key] = entry
        self._save_cache()

    def set_deployment_tags(
            self,
            repository: str,
            image: str,
            etag: str,
            data: Any,
            ttl: Optional[int] = None,
    ) -> None:
        """
        Сохраняет данные тегов развертываний в кэш с специальной стратегией

        Args:
            repository: Имя репозитория
            image: Образ для поиска
            etag: ETag заголовок
            data: Данные для кэширования
            ttl: Время жизни в секундах (по умолчанию default_ttl)
        """
        if ttl is None:
            ttl = self.default_ttl

        expires_at = datetime.now() + timedelta(seconds=ttl)

        entry = CacheEntry(
            url=f"/deployments/tags?repository={repository}&image={image}",
            etag=etag,
            data=data,
            timestamp=datetime.now(),
            expires_at=expires_at,
        )

        key = self._get_deployment_tags_cache_key(repository, image)
        self._cache[key] = entry
        self._save_cache()

    def invalidate(self, url: str, method: str = "GET") -> None:
        """
        Удаляет запись из кэша

        Args:
            url: URL запроса
            method: HTTP метод
        """
        key = self._get_cache_key(url, method)
        if key in self._cache:
            del self._cache[key]
            self._save_cache()

    def invalidate_deployment_tags(self, repository: str, image: str) -> None:
        """
        Удаляет запись тегов развертываний из кэша

        Args:
            repository: Имя репозитория
            image: Образ для поиска
        """
        key = self._get_deployment_tags_cache_key(repository, image)
        if key in self._cache:
            del self._cache[key]
            self._save_cache()

    def invalidate_pattern(self, pattern: str) -> None:
        """
        Удаляет записи по паттерну URL

        Args:
            pattern: Паттерн для поиска URL
        """
        keys_to_remove = []
        for key, entry in self._cache.items():
            if pattern in entry.url:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]

        if keys_to_remove:
            self._save_cache()

    def invalidate_deployment_tags_pattern(self, pattern: str) -> None:
        """
        Удаляет записи тегов развертываний по паттерну

        Args:
            pattern: Паттерн для поиска (repository или image)
        """
        keys_to_remove = []
        for key, entry in self._cache.items():
            if key.startswith("deployment_tags:") and pattern in entry.url:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]

        if keys_to_remove:
            self._save_cache()

    def clear(self) -> None:
        """Очищает весь кэш"""
        self._cache.clear()
        self._save_cache()

    def cleanup_expired(self) -> int:
        """
        Удаляет истекшие записи

        Returns:
            Количество удаленных записей
        """
        keys_to_remove = []
        for key, entry in self._cache.items():
            if entry.is_expired():
                keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._cache[key]

        if keys_to_remove:
            self._save_cache()

        return len(keys_to_remove)

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику кэша"""
        total_entries = len(self._cache)
        expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())

        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "active_entries": total_entries - expired_entries,
            "cache_file": str(self.cache_file),
            "cache_dir": str(self.cache_dir),
        }
