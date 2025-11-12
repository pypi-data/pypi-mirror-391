from typing import Any, Dict, List, Optional


class BaseListService:
    """Базовый интерфейс сервисов списка."""

    def list(
            self,
            filters: Optional[List[str]] = None,
            columns_spec: Optional[str] = None,
            no_cache: bool = False,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get(self, key_or_name: str, no_cache: bool = False) -> Optional[Dict[str, Any]]:
        raise NotImplementedError

    def get_available_columns(self) -> List[str]:
        raise NotImplementedError

    def get_default_columns(self) -> List[str]:
        raise NotImplementedError

    def get_completions(
            self,
            column: str,
            current_filters: Optional[List[str]] = None,
            operator: Optional[str] = None,
            prefix: str = "",
    ) -> List[str]:
        raise NotImplementedError
