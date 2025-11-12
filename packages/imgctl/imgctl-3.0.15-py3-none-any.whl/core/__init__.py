"""
Основные модули imgctl

Содержит базовые компоненты для работы с API и конфигурацией.
"""

from .api_client import ImagenariumAPIClient, ImagenariumAPIError
from .config import Config
from .services.servers_service import ServersService, ServerInfo

# Для обратной совместимости
ServerManager = ServersService
from .cache_manager import CacheManager, CacheEntry

__all__ = [
    "Config",
    "ImagenariumAPIClient",
    "ImagenariumAPIError",
    "ServerManager",
    "ServerInfo",
    "CacheManager",
    "CacheEntry",
]
