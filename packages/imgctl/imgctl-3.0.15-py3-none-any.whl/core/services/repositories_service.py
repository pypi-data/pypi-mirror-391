from typing import Any, Dict, List, Optional

from core.api_client import ImagenariumAPIClient
from core.services.base import BaseListService
from utils.dynamic_columns import parse_filters_with_env_support
from utils.formatters import apply_filters, parse_columns_spec

# Импорт для callback прогресса
try:
    from core.progress import ProgressCallback
except ImportError:
    ProgressCallback = Any


class RepositoriesService(BaseListService):
    """Сервис данных для репозиториев."""

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
            repos = self.api_client.get_repositories(no_cache=no_cache, progress=progress)
        except Exception:
            repos = []
        for r in repos:
            rows.append({
                "name": r.get("name", ""),
                "url": r.get("url", ""),
                "status": r.get("status", ""),
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
            requested_columns = parse_columns_spec(
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
            if r.get("name") == key_or_name:
                return r
        return None

    def get_available_columns(self) -> List[str]:
        return ["name", "url", "status"]

    def get_default_columns(self) -> List[str]:
        return ["name", "url", "status"]

    def get_completions(
            self,
            column: str,
            current_filters: Optional[List[str]] = None,
            operator: Optional[str] = None,
            prefix: str = "",
    ) -> List[str]:
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

    def add(self, repository_info: Dict[str, Any]) -> None:
        """
        Добавляет новый репозиторий

        Args:
            repository_info: Словарь с информацией о репозитории (name, url, username, password, offline)
        """
        if not self.api_client:
            raise ValueError("API client не инициализирован")
        self.api_client.add_repository(repository_info)

    def delete(self, repository_id: str) -> None:
        """
        Удаляет репозиторий

        Args:
            repository_id: ID репозитория для удаления
        """
        if not self.api_client:
            raise ValueError("API client не инициализирован")
        self.api_client.delete_repository(repository_id)
