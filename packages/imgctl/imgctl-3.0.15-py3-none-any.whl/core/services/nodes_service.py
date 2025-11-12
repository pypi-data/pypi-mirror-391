from typing import Any, Dict, List, Optional

from core.api_client import ImagenariumAPIClient
from core.services.base import BaseListService
from utils.dynamic_columns import parse_filters_with_env_support, parse_columns_with_env_support
from utils.formatters import apply_filters

# Импорт для callback прогресса
try:
    from core.progress import ProgressCallback
except ImportError:
    ProgressCallback = Any


class NodesService(BaseListService):
    """Сервис данных для нод."""

    def __init__(self, api_client: ImagenariumAPIClient):
        self.api_client = api_client

    def _fetch_rows(
            self,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        if not self.api_client:
            return rows

        try:
            # Используем http_client напрямую для поддержки progress callback
            response = self.api_client.http_client.get(
                "/api/v3/nodes",
                no_cache=no_cache,
                progress=progress,
            )
            nodes = response.json()
        except Exception:
            nodes = []

        for n in nodes:
            rows.append({
                "name": n.get("hostname", ""),
                "ip": n.get("ip", ""),
                "role": n.get("role", ""),
                "availability": n.get("availability", ""),
                "status": n.get("status", ""),
                "dc": n.get("dc", ""),
                "docker_version": n.get("dockerVersion", ""),
                "total_memory": n.get("totalMemory", ""),
                "ssh_port": n.get("sshPort", ""),
                "ssh_user": n.get("sshUser", ""),
                "external_url": n.get("externalUrl", ""),
                "id": n.get("id", ""),
            })
        return rows

    def list(
            self,
            filters: Optional[List[str]] = None,
            columns_spec: Optional[str] = None,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> List[Dict[str, Any]]:
        rows = self._fetch_rows(no_cache=no_cache, progress=progress)
        if filters:
            parsed = parse_filters_with_env_support(filters)
            try:
                rows = apply_filters(rows, parsed)
            except Exception:
                pass

        # Парсим спецификацию столбцов и фильтруем данные
        if columns_spec:
            default_columns = self.get_default_columns()
            all_columns = self.get_available_columns()
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

    def get(
            self,
            key_or_name: str,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> Optional[Dict[str, Any]]:
        for r in self._fetch_rows(no_cache=no_cache, progress=progress):
            if r.get("name") == key_or_name or r.get("id") == key_or_name:
                return r
        return None

    def get_available_columns(self) -> List[str]:
        return [
            "name",
            "ip",
            "role",
            "availability",
            "status",
            "dc",
            "docker_version",
            "total_memory",
            "ssh_port",
            "ssh_user",
            "external_url",
            "id",
        ]

    def get_default_columns(self) -> List[str]:
        return ["name", "ip", "role", "availability", "status"]

    def get_completions(
            self,
            column: str,
            current_filters: Optional[List[str]] = None,
            operator: Optional[str] = None,
            prefix: str = "",
    ) -> List[str]:
        # Для единообразия используем CompletionManager
        rows = self.list(current_filters or None, None, False)
        values: List[str] = []
        for r in rows:
            if column in r and r[column] is not None:
                values.append(str(r[column]))
        uniq = sorted(set(values))
        if operator == "~" and prefix:
            import re
            try:
                pat = re.compile(prefix)
                uniq = [v for v in uniq if pat.search(v)]
            except Exception:
                uniq = [v for v in uniq if prefix in v]
        elif prefix:
            uniq = [v for v in uniq if v.startswith(prefix)]
        return uniq

    def update(
            self,
            node_id: str,
            update_data: Dict[str, Any],
    ) -> None:
        """
        Обновляет информацию о ноде

        Args:
            node_id: ID ноды для обновления
            update_data: Словарь с данными для обновления (ключи в snake_case)
        """
        if not self.api_client:
            raise ValueError("API client не инициализирован")

        # Преобразуем snake_case ключи в camelCase для API
        api_data = {}
        for key, value in update_data.items():
            if key == "external_url":
                api_data["externalUrl"] = value
            elif key == "ssh_port":
                api_data["sshPort"] = value
            elif key == "ssh_user":
                api_data["sshUser"] = value
            else:
                # Остальные ключи оставляем как есть (hostname, role, availability, labels)
                api_data[key] = value

        self.api_client.update_node(node_id, api_data)
