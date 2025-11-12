"""
Сервисы данных для команд и комплитера

Базовые сервисы предоставляют единый интерфейс:
 - list(filters)
 - get(key_or_name)
 - get_available_columns()
 - get_default_columns()
 - get_completions(column, current_filters, operator, prefix)
"""

from .base import BaseListService  # noqa: F401
from .components_service import ComponentsService  # noqa: F401
from .nodes_service import NodesService  # noqa: F401
from .registries_service import RegistriesService  # noqa: F401
from .repositories_service import RepositoriesService  # noqa: F401
from .servers_service import ServersService  # noqa: F401
from .stacks_service import StacksService  # noqa: F401
