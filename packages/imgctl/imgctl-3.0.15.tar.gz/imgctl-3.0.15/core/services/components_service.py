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
    convert_env_filters_to_raw,
)
from utils.formatters import apply_filters


class ComponentsService(BaseListService):
    """Сервис данных для компонентов с кеш-ориентированными операциями."""

    def __init__(self, api_client: ImagenariumAPIClient):
        self.api_client = api_client

    def _image_without_tag(self, image_full: str) -> str:
        """Извлекает образ без тега"""
        return image_full.rsplit(":", 1)[0] if ":" in image_full else image_full

    def extract_tag_from_component(self, comp: Dict[str, Any]) -> str:
        """Извлекает тег из компонента (image или childContainer)"""
        image = comp.get("image", "")
        child = comp.get("childContainer")
        if child and child.get("image"):
            image = child.get("image")
        if ":" in image:
            return image.rsplit(":", 1)[1]
        return "latest"

    def extract_tag_from_task(self, comp: Dict[str, Any]) -> Optional[str]:
        """Извлекает тег из task компонента"""
        tasks = comp.get("tasks", []) or []
        if not tasks:
            return None
        comp_type = comp.get("@c", "")
        if comp_type == ".DeployedRunner":
            child = comp.get("childContainer")
            if not child or not child.get("image"):
                return None
            component_image = child.get("image")
            if ":" not in component_image:
                return None
            _, tag = component_image.rsplit(":", 1)
            return tag if tag else None
        comp_img = comp.get("image", "")
        comp_base = self._image_without_tag(comp_img)
        for t in tasks:
            t_img = t.get("image", "")
            if not t_img or ":" not in t_img:
                continue
            task_base = self._image_without_tag(t_img)
            if task_base and comp_base and task_base == comp_base:
                _, task_tag = t_img.rsplit(":", 1)
                return task_tag if task_tag else None
        # Если не нашли совпадающий task, берем первый
        t_img = tasks[0].get("image", "")
        if not t_img or ":" not in t_img:
            return None
        _, task_tag = t_img.rsplit(":", 1)
        return task_tag if task_tag else None

    def determine_component_status(self, comp: Dict[str, Any]) -> str:
        """Определяет статус компонента на основе его полей"""
        # Проверяем, выключен ли компонент
        if comp.get("off", False):
            return "OFF"

        # Получаем тип компонента
        component_type = comp.get("@c", "")

        # Определяем базовый образ для сравнения
        if component_type == ".DeployedRunner":
            child_container = comp.get("childContainer")
            if child_container and child_container.get("image"):
                comp_image = child_container.get("image")
                comp_base_image = self._image_without_tag(comp_image)
                tasks = comp.get("tasks", []) or []
                if tasks:
                    task_image = tasks[0].get("image", "")
                    task_base_image = self._image_without_tag(task_image)
                    if task_base_image == comp_base_image:
                        component_tag = self.extract_tag_from_component(comp)
                        task_tag = self.extract_tag_from_task(comp)
                        if task_tag and component_tag and component_tag != task_tag:
                            return "BROKEN"
        else:
            # Для .DeployedService сравниваем с image компонента
            comp_image = comp.get("image", "")
            comp_base_image = self._image_without_tag(comp_image)
            tasks = comp.get("tasks", []) or []
            if tasks:
                task_image = tasks[0].get("image", "")
                task_base_image = self._image_without_tag(task_image)
                if task_base_image == comp_base_image:
                    component_tag = self.extract_tag_from_component(comp)
                    task_tag = self.extract_tag_from_task(comp)
                    if task_tag and component_tag and component_tag != task_tag:
                        return "BROKEN"

        # Получаем информацию о репликах
        desired_replicas = comp.get("desiredReplicas", None)
        running_replicas = comp.get("runningReplicas", None)

        if desired_replicas is None or running_replicas is None:
            return comp.get("stackStatus", "UNKNOWN")

        if desired_replicas == 0:
            return "STOPPED"

        if desired_replicas > 0 and running_replicas == 0:
            return "STARTING"

        if running_replicas == desired_replicas:
            return "RUNNING"

        if running_replicas < desired_replicas:
            return f"PARTIAL ({running_replicas}/{desired_replicas})"

        return comp.get("stackStatus", "UNKNOWN")

    def _fetch_rows(
            self,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> List[Dict[str, Any]]:
        if not self.api_client:
            return []

        # Получаем список деплойментов (в async режиме вернется из кеша мгновенно)
        deployments = self.api_client.get_components(no_cache=no_cache, progress=progress)

        rows: List[Dict[str, Any]] = []
        for group in deployments or []:
            namespace = group.get("namespace", "")
            for stack in group.get("stacks", []) or []:
                stack_id = stack.get("stackId", "")
                for comp in stack.get("components", []) or []:
                    name = comp.get("name", "")
                    if not name or name.startswith("checker-"):
                        continue
                    tag = self.extract_tag_from_task(comp) or self.extract_tag_from_component(comp)
                    image = comp.get("image", "")
                    child = comp.get("childContainer")
                    if child and child.get("image"):
                        image = child.get("image")
                    image_name = self._image_without_tag(image)

                    status = self.determine_component_status(comp)
                    repo = comp.get("repo", "")
                    commit = comp.get("commit", "")

                    updated_ts = comp.get("updated", 0)
                    created_ts = comp.get("created", 0)
                    if updated_ts:
                        from datetime import datetime
                        updated_date = datetime.fromtimestamp(updated_ts / 1000).strftime("%Y-%m-%d %H:%M")
                    else:
                        updated_date = ""
                    if created_ts:
                        from datetime import datetime
                        created_date = datetime.fromtimestamp(created_ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        created_date = ""

                    # Берем environmentVariables из самого компонента или из childContainer
                    env_vars = comp.get("environmentVariables") or comp.get("environment")
                    if not env_vars and child:
                        env_vars = child.get("environmentVariables") or child.get("environment")
                    if not env_vars:
                        env_vars = []

                    env_display: Dict[str, Any] = {}
                    env_raw: Dict[str, Any] = {}
                    env_pairs_raw: List[str] = []

                    # Обрабатываем разные форматы environmentVariables
                    if isinstance(env_vars, dict):
                        # Формат: {"KEY1": "value1", "KEY2": "value2"}
                        for k, v in env_vars.items():
                            env_raw[k] = v
                            env_display[k] = v
                            env_pairs_raw.append(f"{k}={v}")
                    elif isinstance(env_vars, list):
                        # Формат: [{"KEY1": "value1"}, {"KEY2": "value2"}] или ["KEY1=value1", "KEY2=value2"]
                        for item in env_vars:
                            if isinstance(item, dict):
                                # Формат списка словарей
                                for k, v in item.items():
                                    env_raw[k] = v
                                    env_display[k] = v
                                    env_pairs_raw.append(f"{k}={v}")
                            elif isinstance(item, str):
                                # Формат списка строк "KEY=value"
                                if "=" in item:
                                    key, value = item.split("=", 1)
                                    env_raw[key] = value
                                    env_display[key] = value
                                    env_pairs_raw.append(item)

                    # Дополнительные поля
                    replicas = comp.get("replicas", "")
                    desired = comp.get("desiredReplicas")
                    running = comp.get("runningReplicas")
                    admin_mode = comp.get("adminMode", False)
                    run_app = comp.get("runApp", False)
                    show_admin_mode = comp.get("showAdminMode", False)
                    off = comp.get("off", False)

                    # Получаем информацию о портах
                    published_ports = comp.get("publishedPorts", [])
                    ports_str = ""
                    if published_ports:
                        ports_list = []
                        for port in published_ports:
                            pub = port.get("publishedPort", "")
                            tgt = port.get("targetPort", "")
                            proto = port.get("protocol", "tcp")
                            if pub:
                                ports_list.append(f"{pub}:{tgt}/{proto}")
                            else:
                                ports_list.append(f"{tgt}/{proto}")
                        ports_str = ", ".join(ports_list)

                    row: Dict[str, Any] = {
                        "name": name,
                        "namespace": namespace,
                        "stack": f"{stack_id}@{namespace}" if stack_id else "",
                        "image": image_name,
                        "tag": tag or "",
                        "status": status,
                        "replicas": str(
                            replicas) if replicas else f"{running or 0}/{desired or 0}" if desired is not None else "",
                        "updated": updated_date,
                        "created": created_date,
                        "repo": repo,
                        "commit": commit,
                        "admin_mode": admin_mode,
                        "run_app": run_app,
                        "show_admin_mode": show_admin_mode,
                        "off": off,
                        "env": ", ".join(env_pairs_raw),
                        "ports": ports_str,
                    }
                    for k, v in env_display.items():
                        row[f"env.{k}"] = v
                    for k, v in env_raw.items():
                        row[f"env.{k}_raw"] = v

                    # Добавляем дополнительные поля из сырых данных (volumes, networks, labels)
                    # Берем из самого компонента или из childContainer
                    volumes = comp.get("volumes", [])
                    if not volumes and child:
                        volumes = child.get("volumes", [])
                    # Форматируем volumes как строку для отображения в списке
                    if volumes:
                        volumes_str = ", ".join([str(v) for v in volumes]) if isinstance(volumes, list) else str(volumes)
                    else:
                        volumes_str = ""
                    row["volumes"] = volumes_str

                    networks = comp.get("networks", [])
                    if not networks and child:
                        networks = child.get("networks", [])
                    # Форматируем networks как строку для отображения в списке
                    if networks:
                        networks_str = ", ".join([str(n) for n in networks]) if isinstance(networks, list) else str(networks)
                    else:
                        networks_str = ""
                    row["networks"] = networks_str

                    labels = comp.get("labels", [])
                    if not labels and child:
                        labels = child.get("labels", [])
                    # Форматируем labels как строку для отображения в списке
                    if labels:
                        if isinstance(labels, dict):
                            labels_str = ", ".join([f"{k}={v}" for k, v in labels.items()])
                        elif isinstance(labels, list):
                            labels_str = ", ".join([str(l) for l in labels])
                        else:
                            labels_str = str(labels)
                    else:
                        labels_str = ""
                    row["labels"] = labels_str

                    rows.append(row)

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
            parsed = convert_env_filters_to_raw(parsed)
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
        """Возвращает компонент с ключами, соответствующими именам столбцов (как в list)"""
        if not self.api_client:
            return None

        # Получаем детальную информацию через API
        comp_raw = self.api_client.get_component_details(
            key_or_name,
            no_cache=no_cache,
            progress=progress,
        )
        if not comp_raw:
            # Пробуем найти в списке (на случай, если имя немного отличается)
            rows = self.list(None, None, no_cache=no_cache)
            for r in rows:
                if r.get("name") == key_or_name or r.get("name", "").split("[", 1)[0] == key_or_name:
                    return r
            return None

        # Преобразуем сырые данные в формат с ключами, соответствующими столбцам
        name = comp_raw.get("name", "")
        if not name:
            return None

        namespace = comp_raw.get("namespace", "")
        stack_id = comp_raw.get("stack_id", "").split("@")[0] if comp_raw.get("stack_id") else ""

        tag = self.extract_tag_from_task(comp_raw) or self.extract_tag_from_component(comp_raw)
        image = comp_raw.get("image", "")
        child = comp_raw.get("childContainer")
        if child and child.get("image"):
            image = child.get("image")
        image_name = self._image_without_tag(image)

        status = self.determine_component_status(comp_raw)
        repo = comp_raw.get("repo", "") or comp_raw.get("stack_repo", "")
        commit = comp_raw.get("commit", "") or comp_raw.get("stack_commit", "")

        updated_ts = comp_raw.get("updated", 0)
        created_ts = comp_raw.get("created", 0)
        if updated_ts:
            from datetime import datetime
            updated_date = datetime.fromtimestamp(updated_ts / 1000).strftime("%Y-%m-%d %H:%M")
        else:
            updated_date = ""
        if created_ts:
            from datetime import datetime
            created_date = datetime.fromtimestamp(created_ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
        else:
            created_date = ""

        # Берем environmentVariables из самого компонента или из childContainer
        env_vars = comp_raw.get("environmentVariables") or comp_raw.get("environment")
        if not env_vars and child:
            env_vars = child.get("environmentVariables") or child.get("environment")
        if not env_vars:
            env_vars = []

        env_display: Dict[str, Any] = {}
        env_raw: Dict[str, Any] = {}
        env_pairs_raw: List[str] = []

        # Обрабатываем разные форматы environmentVariables
        if isinstance(env_vars, dict):
            # Формат: {"KEY1": "value1", "KEY2": "value2"}
            for k, v in env_vars.items():
                env_raw[k] = v
                env_display[k] = v
                env_pairs_raw.append(f"{k}={v}")
        elif isinstance(env_vars, list):
            # Формат: [{"KEY1": "value1"}, {"KEY2": "value2"}] или ["KEY1=value1", "KEY2=value2"]
            for item in env_vars:
                if isinstance(item, dict):
                    # Формат списка словарей (каждый словарь содержит одну пару ключ-значение)
                    for k, v in item.items():
                        env_raw[k] = v
                        env_display[k] = v
                        env_pairs_raw.append(f"{k}={v}")
                elif isinstance(item, str):
                    # Формат списка строк "KEY=value"
                    if "=" in item:
                        key, value = item.split("=", 1)
                        env_raw[key] = value
                        env_display[key] = value
                        env_pairs_raw.append(item)

        replicas = comp_raw.get("replicas", "")
        desired = comp_raw.get("desiredReplicas")
        running = comp_raw.get("runningReplicas")
        admin_mode = comp_raw.get("adminMode", False)
        run_app = comp_raw.get("runApp", False)
        show_admin_mode = comp_raw.get("showAdminMode", False)
        off = comp_raw.get("off", False)

        # Получаем информацию о портах
        published_ports = comp_raw.get("publishedPorts", [])
        ports_str = ""
        if published_ports:
            ports_list = []
            for port in published_ports:
                pub = port.get("publishedPort", "")
                tgt = port.get("targetPort", "")
                proto = port.get("protocol", "tcp")
                if pub:
                    ports_list.append(f"{pub}:{tgt}/{proto}")
                else:
                    ports_list.append(f"{tgt}/{proto}")
            ports_str = ", ".join(ports_list)

        row: Dict[str, Any] = {
            "name": name,
            "namespace": namespace,
            "stack": f"{stack_id}@{namespace}" if stack_id else "",
            "image": image_name,
            "tag": tag or "",
            "status": status,
            "replicas": str(replicas) if replicas else f"{running or 0}/{desired or 0}" if desired is not None else "",
            "updated": updated_date,
            "created": created_date,
            "repo": repo,
            "commit": commit,
            "admin_mode": admin_mode,
            "run_app": run_app,
            "show_admin_mode": show_admin_mode,
            "off": off,
            "env": ", ".join(env_pairs_raw),
            "ports": ports_str,
        }

        # Добавляем динамические ENV столбцы
        for k, v in env_display.items():
            row[f"env.{k}"] = v
        for k, v in env_raw.items():
            row[f"env.{k}_raw"] = v

        # Добавляем STACK_VERSION если есть
        stack_version = comp_raw.get("stack_version")
        if stack_version:
            row["stack_version"] = stack_version

        # Добавляем тип компонента @c из сырых данных
        component_type = comp_raw.get("@c")
        if component_type:
            row["@c"] = component_type

        # Добавляем дополнительные поля из сырых данных (volumes, networks, binds, labels)
        # Эти поля не входят в стандартные столбцы, но важны для детального просмотра
        # Берем из самого компонента или из childContainer
        volumes = comp_raw.get("volumes", [])
        if not volumes and child:
            volumes = child.get("volumes", [])
        if volumes:
            row["_volumes"] = volumes  # Префикс _ для обозначения дополнительных полей

        networks = comp_raw.get("networks", [])
        if not networks and child:
            networks = child.get("networks", [])
        if networks:
            row["_networks"] = networks

        binds = comp_raw.get("binds", [])
        if not binds and child:
            binds = child.get("binds", [])
        if binds:
            row["_binds"] = binds

        labels = comp_raw.get("labels", [])
        if not labels and child:
            labels = child.get("labels", [])
        if labels:
            row["_labels"] = labels

        return row

    def get_available_columns(self) -> List[str]:
        # Базовые колонки в snake_case
        base = [
            "name",
            "namespace",
            "stack",
            "image",
            "tag",
            "stack_version",
            "status",
            "replicas",
            "ports",
            "updated",
            "created",
            "repo",
            "commit",
            "admin_mode",
            "run_app",
            "show_admin_mode",
            "off",
            "volumes",
            "networks",
            "labels",
            "env",
        ]
        # Добавляем динамические env.* из текущих данных
        rows = self.list(None, None, False)
        dynamic = set()
        for r in rows:
            for k in r.keys():
                if k.startswith("env."):
                    dynamic.add(k)
        return sorted(set(base) | dynamic)

    def get_default_columns(self) -> List[str]:
        return ["name", "namespace", "image", "tag", "updated", "status"]

    def truncate_image_name(self, image_name: str, max_length: int = 50) -> str:
        """Обрезает длинные имена образов для лучшего отображения"""
        if len(image_name) <= max_length:
            return image_name

        if "/" in image_name:
            parts = image_name.split("/")
            if len(parts) >= 2:
                registry = parts[0]
                path = "/".join(parts[1:])
                if len(registry) + 1 + 20 <= max_length:
                    return f"{registry}/...{path[-15:]}"
                else:
                    return f"...{image_name[-(max_length - 3):]}"

        return f"...{image_name[-(max_length - 3):]}"

    def get_completions(
            self,
            column: str,
            current_filters: Optional[List[str]] = None,
            operator: Optional[str] = None,
            prefix: str = "",
    ) -> List[str]:
        rows = self.list(current_filters or None, None, False)
        source_col = column
        if column.startswith("env.") and not column.endswith("_raw"):
            raw_candidate = f"{column}_raw"
            if any(raw_candidate in r for r in rows):
                source_col = raw_candidate
        values: List[str] = []
        for r in rows:
            if source_col in r and r[source_col] is not None:
                values.append(str(r[source_col]))
        if column.lower() == "status":
            values.extend([
                "RUNNING", "ACTIVE", "READY", "HEALTHY", "DEPLOYED", "STOPPED", "INACTIVE", "TERMINATED", "FAILED",
                "ERROR", "OFF", "CANCELED", "PENDING", "WAITING", "STARTING", "BROKEN", "UNKNOWN"
            ])
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

    def get_deployment_tags(
            self,
            repository: str,
            image: str,
            no_cache: bool = False,
            progress: Optional[ProgressCallback] = None,
    ) -> List[Dict[str, Any]]:
        """
        Получает список тегов развертываний для указанного репозитория и образа.

        Args:
            repository: Имя репозитория
            image: Имя образа (может быть с префиксом ":tag_prefix__")
            no_cache: Не использовать кеш
            progress: Callback для отображения прогресса (вызывается только при реальных запросах)

        Returns:
            Список словарей с информацией о тегах
        """
        if not self.api_client:
            return []
        try:
            return self.api_client.get_deployment_tags(
                repository, image, no_cache=no_cache, progress=progress
            )
        except Exception:
            return []

    def start(self, name: str) -> None:
        """
        Запускает компонент

        Args:
            name: Имя компонента
        """
        if not self.api_client:
            raise ValueError("API client не инициализирован")
        self.api_client.start_component(name)

    def stop(self, name: str) -> None:
        """
        Останавливает компонент

        Args:
            name: Имя компонента
        """
        if not self.api_client:
            raise ValueError("API client не инициализирован")
        self.api_client.stop_component(name)

    def update(
            self,
            name: str,
            image: str,
            namespace: Optional[str] = None,
            stack: Optional[str] = None,
            component_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Обновляет образ компонента

        Args:
            name: Имя компонента
            image: Новый образ с тегом
            namespace: Namespace компонента (опционально)
            stack: Имя стека (опционально)
            component_data: Данные компонента (опционально)
        """
        if not self.api_client:
            raise ValueError("API client не инициализирован")
        self.api_client.update_component(name, image, namespace, stack, component_data)
