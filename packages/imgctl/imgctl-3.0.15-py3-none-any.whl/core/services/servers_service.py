"""
Сервис для управления серверами «Imagenarium»

Объединяет функциональность управления серверами и их отображения
"""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

import keyring

from core.config import Config
from core.services.base import BaseListService
from utils.dynamic_columns import parse_columns_with_env_support
from utils.formatters import parse_filters, apply_filters


@dataclass
class ServerInfo:
    """Информация о сервере"""

    name: str
    url: str
    username: str
    description: Optional[str] = None
    is_default: bool = False

    def to_dict(self) -> Dict:
        """Преобразует в словарь"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ServerInfo":
        """Создает из словаря"""
        return cls(**data)


class ServersService(BaseListService):
    """Сервис данных для серверов (локальные подключения)."""

    def __init__(self):
        self.config_dir = self._get_config_dir()
        self.servers_file = self.config_dir / "servers.json"
        self._ensure_config_dir()
        self._keyring_available = self._setup_keyring()

    def _get_config_dir(self) -> Path:
        """Получает директорию конфигурации в соответствии с канонами ОС"""
        if os.name == "nt":  # Windows
            config_dir = Path(os.environ.get("APPDATA", "")) / "imgctl"
        else:  # Unix-like (Linux, macOS)
            config_dir = Path.home() / ".config" / "imgctl"

        return config_dir

    def _ensure_config_dir(self):
        """Создает директорию конфигурации если не существует с безопасными правами доступа"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Устанавливаем безопасные права доступа (только для владельца)
        import stat

        if os.name != "nt":  # Не Windows
            # 0o700 = rwx------ (только владелец может читать/писать/выполнять)
            self.config_dir.chmod(stat.S_IRWXU)

    def _load_servers(self) -> Dict[str, ServerInfo]:
        """Загружает список серверов из файла"""
        if not self.servers_file.exists():
            return {}

        try:
            with open(self.servers_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {
                    name: ServerInfo.from_dict(server_data)
                    for name, server_data in data.items()
                }
        except Exception:
            return {}

    def _save_servers(self, servers: Dict[str, ServerInfo]):
        """Сохраняет список серверов в файл с безопасными правами доступа"""
        try:
            import tempfile
            import stat
            import shutil

            data = {name: server.to_dict() for name, server in servers.items()}

            # Создаем временный файл для атомарной записи
            with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.config_dir,
                    delete=False,
                    prefix=".servers_",
                    suffix=".tmp",
            ) as temp_file:
                json.dump(data, temp_file, indent=2, ensure_ascii=False)
                temp_path = temp_file.name

            # Устанавливаем безопасные права доступа
            if os.name != "nt":  # Не Windows
                # 0o600 = rw------- (только владелец может читать/писать)
                os.chmod(temp_path, stat.S_IRUSR | stat.S_IWUSR)

            # Атомарно перемещаем временный файл в целевой
            shutil.move(temp_path, self.servers_file)

        except Exception as e:
            raise Exception(f"Ошибка сохранения серверов: {e}")

    def _setup_keyring(self) -> bool:
        """Настраивает keyring с fallback на файловый бэкенд

        Returns:
            bool: True если keyring доступен и не запрашивает пароль
        """
        try:
            # Сначала пытаемся использовать текущий бэкенд
            backend = keyring.get_keyring()
            backend_name = type(backend).__name__

            # Если используется рекомендуемый бэкенд (macOS Keychain, Windows Credential Manager, SecretService)
            # и он работает, используем его
            if not ("Fail" in backend_name or "Plaintext" in backend_name):
                # Тестируем работу бэкенда
                test_service = "__imgctl_test__"
                test_key = "__test_key__"
                test_value = "__test_value__"

                try:
                    keyring.set_password(test_service, test_key, test_value)
                    retrieved = keyring.get_password(test_service, test_key)
                    keyring.delete_password(test_service, test_key)
                    if retrieved == test_value:
                        # Бэкенд работает, используем его
                        return True
                except Exception:
                    pass

            # Если основной бэкенд не работает, ОБЯЗАТЕЛЬНО устанавливаем PlaintextKeyring
            # Пытаемся из keyring.backends.file, если недоступен - из keyrings.alt.file
            try:
                try:
                    from keyring.backends.file import PlaintextKeyring
                except ImportError:
                    # Fallback на keyrings.alt для старых версий keyring
                    from keyrings.alt.file import PlaintextKeyring

                keyring_file = self.config_dir / "keyring_pass.cfg"
                plaintext_keyring = PlaintextKeyring()
                plaintext_keyring.file_path = str(keyring_file)
                # ВАЖНО: устанавливаем PlaintextKeyring ДО теста
                keyring.set_keyring(plaintext_keyring)

                # Тестируем что PlaintextKeyring работает без запросов
                try:
                    test_service = "__imgctl_test__"
                    test_key = "__test_key__"
                    test_value = "__test_value__"
                    keyring.set_password(test_service, test_key, test_value)
                    retrieved = keyring.get_password(test_service, test_key)
                    keyring.delete_password(test_service, test_key)
                    if retrieved == test_value:
                        return True
                except Exception:
                    # Даже если тест не прошел, PlaintextKeyring уже установлен
                    # Он будет использоваться при следующих вызовах
                    return True  # Возвращаем True, т.к. бэкенд установлен
            except ImportError:
                # Если PlaintextKeyring недоступен, не используем keyring
                return False
            except Exception:
                return False
        except Exception:
            # В случае ошибки все равно пытаемся установить PlaintextKeyring
            try:
                try:
                    from keyring.backends.file import PlaintextKeyring
                except ImportError:
                    from keyrings.alt.file import PlaintextKeyring
                keyring_file = self.config_dir / "keyring_pass.cfg"
                plaintext_keyring = PlaintextKeyring()
                plaintext_keyring.file_path = str(keyring_file)
                keyring.set_keyring(plaintext_keyring)
                return True
            except Exception:
                return False
        return False

    def _get_password(self, server_name: str) -> Optional[str]:
        """Получает пароль из keyring"""
        try:
            return keyring.get_password("imgctl", server_name)
        except Exception:
            return None

    def _set_password(self, server_name: str, password: str):
        """Сохраняет пароль в keyring"""
        try:
            keyring.set_password("imgctl", server_name, password)
        except Exception as e:
            raise Exception(f"Ошибка сохранения пароля: {e}")

    def _delete_password(self, server_name: str):
        """Удаляет пароль из keyring"""
        try:
            keyring.delete_password("imgctl", server_name)
        except Exception:
            pass  # Игнорируем ошибки при удалении

    # ============================================
    # Методы управления серверами (из ServerManager)
    # ============================================

    def add_server(
            self,
            name: str,
            url: str,
            username: str,
            password: str,
            description: Optional[str] = None,
            is_default: bool = False,
    ) -> None:
        """Добавляет новый сервер"""
        servers = self._load_servers()

        if name in servers:
            raise ValueError(f"Сервер с именем '{name}' уже существует")

        # Валидация URL
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL должен начинаться с http:// или https://")

        server = ServerInfo(
            name=name,
            url=url.rstrip("/"),
            username=username,
            description=description,
            is_default=is_default,
        )

        # Если это новый сервер по умолчанию, снимаем флаг с остальных
        if is_default:
            for existing_server in servers.values():
                existing_server.is_default = False

        servers[name] = server
        self._save_servers(servers)
        self._set_password(name, password)

    def remove_server(self, name: str) -> None:
        """Удаляет сервер"""
        servers = self._load_servers()

        if name not in servers:
            raise ValueError(f"Сервер с именем '{name}' не найден")

        del servers[name]
        self._save_servers(servers)
        self._delete_password(name)

    def list_servers(self) -> List[ServerInfo]:
        """Возвращает список серверов (для обратной совместимости)"""
        servers = self._load_servers()
        return list(servers.values())

    def get_server(self, name: str) -> Optional[ServerInfo]:
        """Получает информацию о сервере"""
        servers = self._load_servers()
        return servers.get(name)

    def get_default_server(self) -> Optional[ServerInfo]:
        """Получает сервер по умолчанию

        Если установлен флаг is_default - возвращает его.
        Если серверов только один - автоматически возвращает его.
        Иначе возвращает None.
        """
        servers = self._load_servers()

        # Сначала ищем сервер с флагом is_default
        for server in servers.values():
            if server.is_default:
                return server

        # Если серверов только один, автоматически выбираем его
        if len(servers) == 1:
            return list(servers.values())[0]

        return None

    @staticmethod
    def get_current_server(server: Optional[str] = None) -> Optional[str]:
        """
        Определяет текущий сервер на основе параметров, переменных окружения и настроек.

        Приоритет определения:
        1. Параметр server (если передан)
        2. Переменная окружения IMG_SERVER
        3. Default сервер из конфигурации

        Args:
            server: Имя сервера или URL (из параметров командной строки)

        Returns:
            Имя сервера (строку) или None, если не удалось определить.
            Для URL возвращается имя найденного в конфигурации сервера или hostname:port из URL.
        """
        # 1. Приоритет: параметр server (если передан)
        if server:
            # Если это имя сервера (не URL), возвращаем его
            if not server.startswith(("http://", "https://")):
                return server

            # Если это URL, пытаемся найти соответствующий сервер в конфигурации
            try:
                svc = ServersService()
                servers = svc.list_servers()
                for s in servers:
                    if s.url.rstrip("/") == server.rstrip("/"):
                        # Найден сервер в конфигурации - возвращаем его имя
                        return s.name
            except Exception:
                pass

            # Сервер не найден в конфигурации - извлекаем hostname:port из URL
            parsed = urlparse(server)
            if parsed.port:
                return f"{parsed.hostname}:{parsed.port}"
            else:
                return parsed.hostname or parsed.netloc

        # 2. Приоритет: переменная окружения IMG_SERVER
        env_server = os.getenv("IMG_SERVER")
        if env_server:
            # Если это имя сервера (не URL), возвращаем его
            if not env_server.startswith(("http://", "https://")):
                return env_server

            # Если это URL, пытаемся найти соответствующий сервер в конфигурации
            try:
                svc = ServersService()
                servers = svc.list_servers()
                for s in servers:
                    if s.url.rstrip("/") == env_server.rstrip("/"):
                        # Найден сервер в конфигурации - возвращаем его имя
                        return s.name
            except Exception:
                pass

            # Сервер не найден в конфигурации - извлекаем hostname:port из URL
            parsed = urlparse(env_server)
            if parsed.port:
                return f"{parsed.hostname}:{parsed.port}"
            else:
                return parsed.hostname or parsed.netloc

        # 3. Приоритет: default сервер из конфигурации
        try:
            svc = ServersService()
            default_server = svc.get_default_server()
            if default_server:
                return default_server.name
        except Exception:
            pass

        return None

    @staticmethod
    def get_config(
            server: Optional[str] = None,
            username: Optional[str] = None,
            password: Optional[str] = None,
            config_path: Optional[str] = None,
    ) -> Config:
        """
        Определяет и возвращает конфигурацию на основе параметров, переменных окружения и настроек.

        Приоритет определения:
        1. Прямое подключение через параметры (server + username + password)
        2. Подключение через сохраненный сервер (server без username/password)
        3. Прямое подключение через переменные окружения (IMG_SERVER + IMG_USERNAME + IMG_PASSWORD)
        4. Подключение через переменную окружения IMG_SERVER (как имя сервера или URL)
        5. Default сервер из конфигурации
        6. Fallback на старую конфигурацию из файла

        Args:
            server: Имя сервера или URL (из параметров командной строки)
            username: Имя пользователя (для прямого подключения)
            password: Пароль (для прямого подключения)
            config_path: Путь к файлу конфигурации (для fallback)

        Returns:
            Объект Config с настроенной конфигурацией

        Raises:
            ValueError: Если не удалось определить конфигурацию или для URL нужны учетные данные
        """
        from rich.console import Console

        console = Console()
        env_server = os.getenv("IMG_SERVER")
        env_username = os.getenv("IMG_USERNAME")
        env_password = os.getenv("IMG_PASSWORD")

        cfg = None

        # 1. Прямое подключение через параметры командной строки
        if server and username and password:
            cfg = Config()
            cfg.server = server
            cfg.username = username
            cfg.password = password
            return cfg

        # 2. Подключение через сохраненный сервер
        if server:
            try:
                servers_service = ServersService()
                cfg = servers_service.get_config_for_server(server)
                return cfg
            except ValueError:
                # Сервер не найден, продолжим проверку других вариантов
                pass

        # 3. Прямое подключение через переменные окружения
        if env_server and env_username and env_password:
            cfg = Config()
            cfg.server = env_server
            cfg.username = env_username
            cfg.password = env_password
            return cfg

        # 4. Подключение через переменную окружения IMG_SERVER
        if env_server:
            if env_server.startswith(("http://", "https://")):
                # Это URL, нужны учетные данные
                if env_username and env_password:
                    cfg = Config()
                    cfg.server = env_server
                    cfg.username = env_username
                    cfg.password = env_password
                    return cfg
                else:
                    console.print(
                        "[red]Для URL в IMG_SERVER требуются IMG_USERNAME и IMG_PASSWORD[/red]"
                    )
                    raise ValueError("Для URL в IMG_SERVER требуются учетные данные")
            else:
                # Это имя сервера
                try:
                    servers_service = ServersService()
                    cfg = servers_service.get_config_for_server(env_server)
                    return cfg
                except ValueError:
                    # Сервер не найден, продолжим проверку
                    pass

        # 5. Использование сервера по умолчанию
        try:
            servers_service = ServersService()
            cfg = servers_service.get_config_for_server()
            return cfg
        except ValueError:
            # Нет default сервера, переходим к fallback
            pass

        # 6. Fallback на старую конфигурацию из файла
        cfg = Config()
        if config_path:
            cfg.load_from_file(config_path)
        cfg.load_from_env()

        # Если конфигурация не загружена, пробуем загрузить из файла по умолчанию
        if not cfg.username or not cfg.password:
            cfg.load_from_file()

        # Проверяем, что конфигурация валидна
        if not cfg.server or not cfg.username or not cfg.password:
            raise ValueError(
                "Не удалось определить конфигурацию сервера. "
                "Добавьте сервер командой 'servers add' или укажите параметры подключения."
            )

        return cfg

    def set_default_server(self, name: str) -> None:
        """Устанавливает сервер по умолчанию"""
        servers = self._load_servers()

        if name not in servers:
            raise ValueError(f"Сервер с именем '{name}' не найден")

        # Снимаем флаг с остальных серверов
        for server in servers.values():
            server.is_default = False

        # Устанавливаем флаг для указанного сервера
        servers[name].is_default = True
        self._save_servers(servers)

    def get_config_for_server(self, server_name: Optional[str] = None) -> Config:
        """Получает конфигурацию для указанного сервера"""
        config = Config()

        if server_name:
            server = self.get_server(server_name)
            if not server:
                raise ValueError(f"Сервер '{server_name}' не найден")
        else:
            server = self.get_default_server()
            if not server:
                raise ValueError(
                    "Нет сервера по умолчанию. Добавьте сервер командой 'servers add'"
                )

        config.server = server.url
        config.username = server.username
        config.password = self._get_password(server.name)

        return config

    def update_server(self, name: str, **kwargs) -> None:
        """Обновляет информацию о сервере"""
        servers = self._load_servers()

        if name not in servers:
            raise ValueError(f"Сервер с именем '{name}' не найден")

        server = servers[name]

        # Обновляем поля
        for key, value in kwargs.items():
            if hasattr(server, key) and value is not None:
                setattr(server, key, value)

        # Если устанавливается как сервер по умолчанию
        if kwargs.get("is_default", False):
            for existing_server in servers.values():
                existing_server.is_default = False
            server.is_default = True

        self._save_servers(servers)

        # Обновляем пароль если указан
        if "password" in kwargs:
            self._set_password(name, kwargs["password"])

    # ============================================
    # Методы BaseListService (для отображения)
    # ============================================

    def _fetch_rows(self, no_cache: bool = False) -> List[Dict[str, Any]]:
        """Получает данные серверов для отображения"""
        rows: List[Dict[str, Any]] = []
        servers = self.list_servers()
        for s in servers:
            rows.append({
                "name": s.name,
                "url": s.url,
                "username": s.username,
                "description": getattr(s, "description", ""),
                "default": getattr(s, "is_default", False),
            })
        return rows

    def list(
            self,
            filters: Optional[List[str]] = None,
            columns_spec: Optional[str] = None,
            no_cache: bool = False,
    ) -> List[Dict[str, Any]]:
        rows = self._fetch_rows(no_cache=no_cache)

        # Применяем фильтры
        if filters:
            parsed = parse_filters(filters)
            try:
                rows = apply_filters(rows, parsed)
            except Exception:
                pass

        # Парсим спецификацию столбцов и фильтруем данные
        if columns_spec:
            default_columns = self.get_default_columns()
            all_columns = self.get_available_columns()
            # Добавляем динамические столбцы из данных
            if rows:
                all_available_columns = set(all_columns)
                for row in rows:
                    all_available_columns.update(row.keys())
                all_columns = list(all_available_columns)
            requested_columns = parse_columns_with_env_support(
                columns_spec, default_columns, all_columns
            )
            # Фильтруем данные по выбранным столбцам
            filtered_rows = []
            for row in rows:
                filtered_row = {col: row.get(col, "") for col in requested_columns}
                filtered_rows.append(filtered_row)
            return filtered_rows

        return rows

    def get(self, key_or_name: str, no_cache: bool = False) -> Optional[Dict[str, Any]]:
        for r in self.list(None, None, no_cache=no_cache):
            if r.get("name") == key_or_name:
                return r
        return None

    def get_available_columns(self) -> List[str]:
        return ["name", "url", "username", "description", "default"]

    def get_default_columns(self) -> List[str]:
        return ["name", "url", "username"]

    def get_completions(
            self,
            column: str,
            current_filters: Optional[List[str]] = None,
            operator: Optional[str] = None,
            prefix: str = "",
    ) -> List[str]:
        values = []
        for r in self.list(current_filters or None, None, False):
            if column in r and r[column] is not None:
                values.append(str(r[column]))
        uniq = sorted(set(values))
        if prefix:
            uniq = [v for v in uniq if v.startswith(prefix)]
        return uniq


def get_server_name_from_config_or_url(server: Optional[str] = None, server_url: Optional[str] = None) -> Optional[str]:
    """
    Определяет имя сервера для кеша

    Args:
        server: Имя сервера или URL (если передан --server)
        server_url: URL сервера из конфигурации

    Returns:
        Имя сервера для использования в кеше (имя из конфигурации или hostname:port из URL)
    """
    # Если server передан и это не URL (начинается с http:// или https://)
    if server and not server.startswith(("http://", "https://")):
        # Это имя сервера - возвращаем его
        return server

    # Если server передан и это URL
    if server and server.startswith(("http://", "https://")):
        # Пытаемся найти сервер в конфигурации по URL
        try:
            svc = ServersService()
            servers = svc.list_servers()
            for s in servers:
                if s.url.rstrip("/") == server.rstrip("/"):
                    # Найден сервер в конфигурации - используем его имя
                    return s.name
        except Exception:
            pass

        # Сервер не найден в конфигурации - используем hostname:port из URL
        parsed = urlparse(server)
        if parsed.port:
            return f"{parsed.hostname}:{parsed.port}"
        else:
            return parsed.hostname or parsed.netloc

    # Если server не передан, но есть server_url (из конфигурации)
    if server_url:
        # Пытаемся найти сервер в конфигурации по URL
        try:
            svc = ServersService()
            servers = svc.list_servers()
            for s in servers:
                if s.url.rstrip("/") == server_url.rstrip("/"):
                    # Найден сервер в конфигурации - используем его имя
                    return s.name
        except Exception:
            pass

        # Сервер не найден в конфигурации - используем hostname:port из URL
        parsed = urlparse(server_url)
        if parsed.port:
            return f"{parsed.hostname}:{parsed.port}"
        else:
            return parsed.hostname or parsed.netloc

    return None


# Для обратной совместимости экспортируем ServerManager и ServerInfo
ServerManager = ServersService  # type: ignore
