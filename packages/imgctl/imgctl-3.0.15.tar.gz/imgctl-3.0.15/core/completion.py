"""
Модуль для поддержки bash completion
"""

from typing import List, Dict, Any, Optional

from core.api_client import ImagenariumAPIClient
from core.services import (
    ComponentsService,
    StacksService,
    NodesService,
    RegistriesService,
    RepositoriesService,
    ServersService,
)


class CompletionManager:
    """Менеджер для bash completion - работает только через сервисы"""

    def __init__(
            self,
            server_name: Optional[str] = None,
            cache_dir: Optional[str] = None,
            api_client: Optional[ImagenariumAPIClient] = None
    ):
        # cache_dir параметр оставлен для обратной совместимости, но не используется
        self.server_name = server_name or self._get_default_server_name()
        # Используем переданный API клиент для переиспользования кэша
        self._cached_api_client = api_client

    def _get_default_server_name(self) -> str:
        """Получает имя сервера по умолчанию"""
        try:
            servers_service = ServersService()
            default_server = servers_service.get_default_server()
            if default_server:
                return default_server.name
            else:
                return "default"
        except Exception:
            return "default"

    def _get_current_server_name(self) -> str:
        """Получает текущий сервер из переменных окружения или использует сохраненный"""
        # Используем централизованный метод из ServersService
        current_server = ServersService.get_current_server(server=self.server_name)
        # Если метод вернул None или пустую строку, используем сохраненный server_name как fallback
        return current_server or self.server_name or "default"

    def _get_api_client(self) -> Optional[ImagenariumAPIClient]:
        """Получает API клиент для запросов"""
        # Используем кэшированный API клиент, если он был передан
        if self._cached_api_client is not None:
            return self._cached_api_client

        # Иначе создаем новый (fallback для случаев вне shell)
        try:
            servers_service = ServersService()
            # Определяем текущий сервер динамически (может измениться через переменные окружения)
            current_server = self._get_current_server_name()
            config = servers_service.get_config_for_server(current_server)
            # async_mode только в shell режиме
            import os
            is_shell_mode = os.getenv("IMGCTL_SHELL_MODE") == "1"

            return ImagenariumAPIClient(
                config=config,
                async_mode=is_shell_mode,
                server_name=current_server
            )
        except Exception:
            return None

    # ============================
    # ДАННЫЕ ДЛЯ РЕПЛ КОМПЛИШЕНА
    # ============================

    def _get_components_dataset(self, no_cache: bool = False) -> List[Dict[str, Any]]:
        """Совместимость: теперь данные берутся из сервиса компонентов."""
        try:
            api_client = self._get_api_client()
            if not api_client:
                return []
            svc = ComponentsService(api_client=api_client)
            return svc.list(no_cache=no_cache)
        except Exception:
            return []

    def _get_stacks_dataset(self, no_cache: bool = False) -> List[Dict[str, Any]]:
        """Совместимость: теперь данные берутся из сервиса стеков."""
        try:
            api_client = self._get_api_client()
            if not api_client:
                return []
            svc = StacksService(api_client=api_client)
            return svc.list(no_cache=no_cache)
        except Exception:
            return []

    def get_dynamic_env_keys(self) -> List[str]:
        """Возвращает список динамических ENV.* ключей по текущему стенду."""
        keys = set()
        for row in self._get_components_dataset():
            for k in row.keys():
                # Проверяем оба варианта: env.* (snake_case) и ENV.* (uppercase)
                if (k.startswith("env.") or k.startswith("ENV.")) and not k.endswith("_raw") and not k.endswith("_RAW"):
                    # Преобразуем в UPPER_CASE для единообразия
                    key_upper = k.upper() if not k.startswith("ENV.") else k
                    keys.add(key_upper)
        return sorted(keys)

    def get_dynamic_param_keys(self) -> List[str]:
        """Возвращает список динамических PARAMS.* ключей по текущему стенду."""
        keys = set()
        for row in self._get_stacks_dataset():
            for k in row.keys():
                if k.startswith("PARAMS.") and not k.endswith("_RAW"):
                    keys.add(k)
        return sorted(keys)

    def _get_service(self, command: str):
        api_client = self._get_api_client()
        if not api_client:
            return None

        if command == "components":
            return ComponentsService(api_client=api_client)
        if command == "stacks":
            return StacksService(api_client=api_client)
        if command == "nodes":
            return NodesService(api_client=api_client)
        if command == "registries":
            return RegistriesService(api_client=api_client)
        if command == "repositories":
            return RepositoriesService(api_client=api_client)
        if command == "servers":
            return ServersService()
        return None

    def get_columns_for_command(self, command: str) -> List[str]:
        """Возвращает доступные столбцы через сервис соответствующей команды."""
        svc = self._get_service(command)
        if not svc:
            return []
        try:
            return svc.get_available_columns()
        except Exception:
            return []

    def get_column_values(
            self,
            command: str,
            column: str,
            current_filters: List[str],
            operator: Optional[str] = None,
            prefix: str = "",
    ) -> List[str]:
        """Возвращает уникальные значения столбца с учетом активных фильтров и префикса.

        Для ENV./PARAMS. используется *_RAW для корректной фильтрации.
        """
        svc = self._get_service(command)
        if not svc:
            return []
        try:
            return svc.get_completions(column=column, current_filters=current_filters, operator=operator,
                                       prefix=prefix)[:200]
        except Exception:
            return []

    def get_components(self, no_cache: bool = False) -> List[str]:
        """Получает список имен компонентов через сервис"""
        try:
            api_client = self._get_api_client()
            if not api_client:
                return []
            svc = ComponentsService(api_client=api_client)
            components = svc.list(no_cache=no_cache)
            names = []
            for comp in components:
                name = comp.get("name", "")
                if name and not name.startswith("checker-"):
                    names.append(name)
            return sorted(list(set(names)))
        except Exception:
            return []

    def get_stacks(self, no_cache: bool = False) -> List[str]:
        """Получает список имен стеков через сервис"""
        try:
            api_client = self._get_api_client()
            if not api_client:
                return []
            svc = StacksService(api_client=api_client)
            stacks = svc.list(no_cache=no_cache)
            names = [stack.get("name", "") for stack in stacks if stack.get("name")]
            return sorted(list(set(names)))
        except Exception:
            return []

    def get_nodes(self, no_cache: bool = False) -> List[str]:
        """Получает список имен нод через сервис"""
        try:
            api_client = self._get_api_client()
            if not api_client:
                return []
            svc = NodesService(api_client=api_client)
            nodes = svc.list(no_cache=no_cache)
            names = [node.get("name", "") for node in nodes if node.get("name")]
            return sorted(list(set(names)))
        except Exception:
            return []

    def get_registries(self, no_cache: bool = False) -> List[str]:
        """Получает список имен реестров через сервис"""
        try:
            api_client = self._get_api_client()
            if not api_client:
                return []
            svc = RegistriesService(api_client=api_client)
            registries = svc.list(no_cache=no_cache)
            names = [reg.get("name", "") for reg in registries if reg.get("name")]
            return sorted(list(set(names)))
        except Exception:
            return []

    def get_repositories(self, no_cache: bool = False) -> List[str]:
        """Получает список имен репозиториев через сервис"""
        try:
            api_client = self._get_api_client()
            if not api_client:
                return []
            svc = RepositoriesService(api_client=api_client)
            repositories = svc.list(no_cache=no_cache)
            names = [repo.get("name", "") for repo in repositories if repo.get("name")]
            return sorted(list(set(names)))
        except Exception:
            return []

    def get_servers(self, no_cache: bool = False) -> List[str]:
        """Получает список имен серверов через сервис"""
        try:
            svc = ServersService()
            servers = svc.list(no_cache=no_cache)
            names = [server.get("name", "") for server in servers if server.get("name")]
            return sorted(list(set(names)))
        except Exception:
            return []

    def get_namespaces(self, no_cache: bool = False) -> List[str]:
        """Получает список уникальных namespace через сервис"""
        try:
            api_client = self._get_api_client()
            if not api_client:
                return []
            svc = ComponentsService(api_client=api_client)
            components = svc.list(no_cache=no_cache)
            namespaces = {comp.get("namespace", "") for comp in components if comp.get("namespace")}
            return sorted(list(namespaces))
        except Exception:
            return []

    def get_available_columns(self, command: str) -> List[str]:
        """Совместимый метод: делегирует в сервис соответствующей команды."""
        return self.get_columns_for_command(command)

    def get_command_options(self, command: str, subcommand: str = "list") -> List[str]:
        """Получает доступные опции подкоманды динамически из Click."""
        try:
            from cli.main import main as click_main
            grp = click_main.commands.get(command)
            if not grp:
                return []
            with click_main.make_context("imgctl", [command, subcommand]) as ctx:
                cmd = grp.get_command(ctx, subcommand) if hasattr(grp, "get_command") else None
            if not cmd or not hasattr(cmd, "params"):
                return []
            opts: List[str] = []
            for p in cmd.params:
                if getattr(p, "opts", None):
                    opts.extend(p.opts)
                if getattr(p, "secondary_opts", None):
                    opts.extend(p.secondary_opts)
            # Уникальные, длинные впереди
            long_opts = sorted({o for o in opts if o.startswith("--")})
            short_opts = sorted({o for o in opts if o.startswith("-") and not o.startswith("--")})
            return long_opts + short_opts
        except Exception:
            return []
