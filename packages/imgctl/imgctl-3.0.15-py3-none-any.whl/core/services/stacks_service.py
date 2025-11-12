from typing import Any, Dict, List, Optional

from core.api_client import ImagenariumAPIClient
from core.services.base import BaseListService

# Импорт для callback прогресса
try:
    from core.progress import ProgressCallback
except ImportError:
    ProgressCallback = Any
from utils.dynamic_columns import (
    parse_columns_with_env_support,
    parse_filters_with_env_support,
    convert_params_filters_to_raw,
)
from utils.formatters import apply_filters


class StacksService(BaseListService):
    """Сервис данных для стеков с кеш-ориентированными операциями."""

    def __init__(self, api_client: ImagenariumAPIClient):
        self.api_client = api_client

    def _fetch_rows(
            self,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> List[Dict[str, Any]]:
        if not self.api_client:
            return []
        deployments = self.api_client.get_components(no_cache=no_cache, progress=progress)
        stacks = {}
        for component in deployments or []:
            stacks_data = component.get("stacks", []) or []
            if not stacks_data:
                continue
            for stack_data in stacks_data:
                stack_id = stack_data.get("stackId")
                if not stack_id:
                    continue
                namespace = stack_data.get("namespace", "N/A")
                key = f"{stack_id}@{namespace}"
                if key not in stacks:
                    stacks[key] = {
                        "name": key,
                        "namespace": namespace,
                        "version": stack_data.get("version", "N/A"),
                        "repo": stack_data.get("repo", "N/A"),
                        "commit": stack_data.get("commit", "N/A"),
                        "time": stack_data.get("timestamp", ""),
                        "tag": stack_data.get("tag", ""),
                        "params": ", ".join([f"{k}={v}" for k, v in (stack_data.get("params", {}) or {}).items()]),
                        "status": stack_data.get("status", "UNKNOWN"),
                    }
                # динамические params.*
                for k, v in (stack_data.get("params", {}) or {}).items():
                    stacks[key][f"params.{k}"] = v
        return list(stacks.values())

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
            parsed = convert_params_filters_to_raw(parsed)
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

    def get(
            self,
            key_or_name: str,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> Optional[Dict[str, Any]]:
        rows = self.list(None, None, no_cache=no_cache, progress=progress)
        for r in rows:
            if r.get("name") == key_or_name or r.get("name", "").split("[", 1)[0] == key_or_name:
                return r
        return None

    def get_available_columns(self) -> List[str]:
        base = [
            "name",
            "namespace",
            "version",
            "status",
            "repo",
            "commit",
            "time",
            "tag",
            "params",
            "components",
        ]
        rows = self.list(None, None, False)
        dynamic = set()
        for r in rows:
            for k in r.keys():
                if k.startswith("params."):
                    dynamic.add(k)
        return sorted(set(base) | dynamic)

    def get_default_columns(self) -> List[str]:
        return ["name", "namespace", "version", "status"]

    def get_completions(
            self,
            column: str,
            current_filters: Optional[List[str]] = None,
            operator: Optional[str] = None,
            prefix: str = "",
    ) -> List[str]:
        rows = self.list(current_filters or None, None, False)
        source_col = column
        if column.startswith("params.") and not column.endswith("_raw"):
            raw_candidate = f"{column}_raw"
            if any(raw_candidate in r for r in rows):
                source_col = raw_candidate
        values: List[str] = []
        for r in rows:
            if source_col in r and r[source_col] is not None:
                values.append(str(r[source_col]))
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
