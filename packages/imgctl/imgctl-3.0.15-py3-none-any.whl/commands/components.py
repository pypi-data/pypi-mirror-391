"""
Команды для управления компонентами
"""

from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

from core.api_client import ImagenariumAPIError
from core.services.components_service import ComponentsService
from utils.formatters import format_table, format_output, show_console_header
from utils.verbose import verbose_print, set_verbose

console = Console()


def _parse_string_value(value: str):
    """
    Пытается определить тип значения из строки

    Args:
        value: Строковое значение

    Returns:
        Значение с правильным типом (int, float, bool или str)
    """
    typed_value = value
    try:
        # Пробуем преобразовать в число
        if "." in value:
            typed_value = float(value)
        else:
            typed_value = int(value)
    except ValueError:
        # Если не число, пробуем bool
        if value.lower() in ("true", "false"):
            typed_value = value.lower() == "true"
    return typed_value


def _get_api_client(verbose: bool = False, ctx=None):
    """Создает API клиент с заданными параметрами"""
    from cli.main import get_api_client

    # Получаем параметры из контекста если доступен
    if ctx and hasattr(ctx, "obj"):
        server = ctx.obj.get("server")
        username = ctx.obj.get("username")
        password = ctx.obj.get("password")
        config = ctx.obj.get("config")
        return get_api_client(
            verbose=verbose,
            server=server,
            username=username,
            password=password,
            config=config,
        )
    else:
        return get_api_client(verbose=verbose)


@click.group()
def cli():
    """Управление компонентами приложений"""
    pass


@cli.command("list")
@click.option("--limit", "-l", type=int, help="Ограничить количество записей")
@click.option("--no-cache", is_flag=True, help="Отключить кэширование")
@click.option(
    "--columns",
    help='Столбцы для отображения. Форматы: "NAME,STATUS" или "+REPLICAS,-NAMESPACE". Доступные: NAME, NAMESPACE, STACK, IMAGE, TAG, STACK_VERSION, STATUS, REPLICAS, PORTS, UPDATED, CREATED, REPO, COMMIT, ADMIN_MODE, RUN_APP, SHOW_ADMIN_MODE, OFF, NETWORKS, ENV, ENV.<переменная>',
)
@click.option(
    "--filter",
    multiple=True,
    help="Фильтрация данных. Формат: COLUMN=value, COLUMN!=value, COLUMN~pattern. Примеры: STATUS=RUNNING, NAMESPACE!=test, NAME~postgres, ENV~database, ENV.DB_HOST=localhost",
)
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option(
    "--output",
    "-o",
    help='Формат вывода данных: json, yaml, tsv, или template (например: "{NAME} - {STATUS}")',
)
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def list_components(ctx, limit, no_cache, columns, filter, no_headers, output, verbose):
    """Показывает список развернутых компонентов

    По умолчанию: NAME, NAMESPACE, IMAGE, TAG, UPDATED, STATUS. Дополнительные: STACK, STACK_VERSION, REPLICAS, PORTS, CREATED, REPO, COMMIT, ADMIN_MODE, RUN_APP, SHOW_ADMIN_MODE, OFF, NETWORKS, ENV, ENV.<переменная>
    """
    try:
        # Устанавливаем режим verbose для логирования
        set_verbose(verbose)

        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли (скрываем при --no-headers или --output)
        show_console_header(api, show_header=not (no_headers or output))

        # Сервис данных
        svc = ComponentsService(api_client=api)

        # Используем callback для прогресс-бара (вызывается только при реальных запросах)
        from core.progress import create_progress_context

        with create_progress_context(
                "Получение списка компонентов...",
        ) as progress_callback:
            # Получаем данные и применяем фильтры на уровне сервиса
            # columns_spec передается в list, где он парсится и применяется
            rows = svc.list(
                filters=list(filter) if filter else None,
                columns_spec=columns,
                no_cache=no_cache,
                progress=progress_callback,
            )

        if not rows:
            console.print("Компоненты не найдены")
            return

        # Ограничение
        if limit:
            rows = rows[:limit]

        # Определяем столбцы для вывода (данные уже отфильтрованы в list)
        from utils.formatters import parse_filters

        # Если columns указан, используем столбцы из данных, иначе default
        if columns and rows:
            requested_columns = list(rows[0].keys()) if rows else svc.get_default_columns()
        else:
            requested_columns = svc.get_default_columns()

        # Данные уже отфильтрованы по столбцам в list
        filtered_data = rows

        # Вывод
        if not output or output == "table":
            highlight_filters = parse_filters(list(filter)) if filter else None
            # Используем truncate из сервиса для image
            # Подсветку имен компонентов делаем ПОСЛЕ подсветки фильтров в format_table
            for row in filtered_data:
                if "image" in row:
                    row["image"] = svc.truncate_image_name(row["image"])
            format_table(
                filtered_data,
                columns=requested_columns,
                no_headers=no_headers,
                highlight_filters=highlight_filters,
            )
        else:
            format_output(filtered_data, output, columns=requested_columns)

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка получения списка компонентов: {e}[/red]")
        raise click.Abort()


@cli.command("stop")
@click.argument("name")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.pass_context
def stop_component(ctx, name, no_headers):
    """Останавливает компонент"""
    try:
        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=False, ctx=ctx)

        # Показываем заголовок консоли
        show_console_header(api, show_header=not no_headers)

        console.print(f"[blue]Остановка компонента {name}...[/blue]")
        svc = ComponentsService(api_client=api)
        svc.stop(name)
        console.print(f"[green]Компонент {name} успешно остановлен[/green]")

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка остановки компонента: {e}[/red]")
        raise click.Abort()


@cli.command("start")
@click.argument("name")
@click.option("--logs", is_flag=True, help="Показать логи компонента после запуска")
@click.option("--no-cache", is_flag=True, help="Отключить кэширование")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.pass_context
def start_component(ctx, name, logs, no_cache, no_headers):
    """Запускает компонент"""
    try:
        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=False, ctx=ctx)

        # Показываем заголовок консоли
        show_console_header(api, show_header=not no_headers)

        # Запускаем компонент (как в stop - без лишних проверок)
        console.print(f"[blue]Запуск компонента {name}...[/blue]")
        svc = ComponentsService(api_client=api)
        svc.start(name)
        console.print(f"[green]Компонент {name} успешно запущен[/green]")

        # Если запрошены логи, показываем их
        if logs:
            import time
            from commands.logs import stream_logs, get_component_info

            console.print(f"[blue]Показ логов компонента {name}...[/blue]")

            # Небольшая задержка, чтобы компонент успел запуститься
            time.sleep(2)

            try:
                # Получаем информацию о компоненте для получения ID
                # Сначала пробуем использовать кеш
                component_info = get_component_info(api, name, no_cache=False)
                if component_info:
                    # Получаем ID компонента
                    component_id = component_info.get("id")

                    if component_id:
                        try:
                            stream_logs(
                                api,
                                component_id,
                                lines=5,
                                follow=False,
                                level_filter=None,
                            )
                        except Exception as e:
                            error_msg = str(e)
                            # Перехватываем любые ошибки при получении логов (включая timeout)
                            if (
                                    "There is no container, service or task with ID"
                                    in error_msg
                                    or "Read timed out" in error_msg
                                    or "Connection" in error_msg
                            ):
                                console.print(
                                    f"[yellow]Task ID {component_id} не найден, обновляем кеш...[/yellow]"
                                )

                                # Инвалидируем кеш для этого компонента
                                cache_key = f"component_info:{name}"
                                if api.cache:
                                    api.cache.invalidate(cache_key)
                                    console.print(
                                        f"[dim]Кеш для {name} инвалидирован[/dim]"
                                    )

                                # Получаем свежую информацию о компоненте
                                console.print(
                                    f"[blue]Повторный поиск компонента {name}...[/blue]"
                                )
                                component_info = get_component_info(
                                    api, name, no_cache=True
                                )

                                if not component_info:
                                    console.print(
                                        f"[red]Компонент {name} не найден после обновления кеша[/red]"
                                    )
                                    return

                                # Получаем новый ID компонента
                                new_component_id = component_info.get("id")

                                if not new_component_id:
                                    console.print(
                                        f"[red]Не удалось получить новый ID компонента {name}[/red]"
                                    )
                                    return

                                console.print(
                                    f"[green]Найден компонент: {name} (ID: {new_component_id})[/green]"
                                )

                                # Повторяем попытку с новым ID
                                stream_logs(
                                    api,
                                    new_component_id,
                                    lines=5,
                                    follow=False,
                                    level_filter=None,
                                )
                            else:
                                # Если это другая ошибка, просто пробрасываем её
                                raise
                    else:
                        console.print(
                            f"[red]Не удалось получить ID компонента {name}[/red]"
                        )
                else:
                    console.print(
                        f"[red]Компонент {name} не найден для логирования[/red]"
                    )
            except Exception as e:
                console.print(f"[red]Ошибка показа логов: {e}[/red]")

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка запуска компонента: {e}[/red]")
        raise click.Abort()


@cli.command("get")
@click.argument("name")
@click.option("--no-cache", is_flag=True, help="Отключить кэширование")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def get_component(ctx, name, no_cache, verbose):
    """Показывает детальную информацию о компоненте"""
    try:
        # Устанавливаем режим verbose для логирования
        set_verbose(verbose)

        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли
        show_console_header(api)

        # Используем сервис для получения данных в унифицированном формате
        svc = ComponentsService(api_client=api)

        # Используем callback для прогресс-бара (вызывается только при реальных запросах)
        from core.progress import create_progress_context

        with create_progress_context(
                "Получение информации о компонентах...",
        ) as progress_callback:
            component = svc.get(name, no_cache=no_cache, progress=progress_callback)

        if not component:
            console.print(f"Компонент '{name}' не найден")
            return

        # Выводим основную информацию (компонент уже в унифицированном формате с ключами NAME, NAMESPACE и т.д.)

        # Основные параметры (данные в snake_case)
        from utils.highlighter import Highlighter

        component_name = component.get("name", "")
        component_namespace = component.get("namespace", "")
        highlighted_name = Highlighter.highlight_component_name(
            component_name, component_namespace
        )
        console.print(f"[bold white]NAME:[/bold white] {highlighted_name}")
        console.print(f"[bold white]NAMESPACE:[/bold white] {component_namespace}")

        # Подсвечиваем имя стека
        stack = component.get("stack", "")
        if stack:
            if "@" in stack:
                stack_name, namespace = stack.split("@", 1)
                console.print(
                    f"[bold white]STACK:[/bold white] {stack_name}[dim]@{namespace}[/dim]"
                )
            else:
                console.print(f"[bold white]STACK:[/bold white] {stack}")

        stack_version = component.get("stack_version", "")
        if stack_version:
            console.print(f"[bold white]STACK_VERSION:[/bold white] {stack_version}")

        # Получаем тег и образ (данные в snake_case)
        image = component.get("image", "")
        tag = component.get("tag", "")

        console.print(f"[bold white]IMAGE:[/bold white] {image}")
        highlighted_tag = Highlighter.highlight_tag(tag)
        console.print(f"[bold white]TAG:[/bold white] {highlighted_tag}")

        # Статус (данные в snake_case)
        status = component.get("status", "")
        styled_status = Highlighter.highlight(status, check_partial=True)
        console.print(f"[bold white]STATUS:[/bold white] {styled_status}")

        # Используем утилиту для вывода полей
        from utils.formatters import print_field

        # Реплики, время создания и обновления
        print_field(component, "replicas")
        print_field(component, "created")
        print_field(component, "updated")

        # Информация о репозитории
        print_field(component, "repo")
        print_field(component, "commit")

        # Дополнительные параметры (булевы значения показываются только если True)
        print_field(component, "admin_mode")
        print_field(component, "run_app")
        print_field(component, "show_admin_mode")
        print_field(component, "off")

        # Порты
        print_field(component, "ports")

        # Переменные окружения
        # Сначала пробуем динамические env.* поля (если есть)
        env_keys = [k for k in component.keys() if k.startswith("env.") and not k.endswith("_raw")]
        if env_keys:
            console.print(f"[bold white]ENV:[/bold white]")
            for key in sorted(env_keys):
                value = component.get(key, "")
                env_name = key.replace("env.", "")
                highlighted_value = Highlighter.highlight_value(value)
                console.print(f"[white]  [bold bright_white]{env_name}[/bold bright_white]: {highlighted_value}[/white]")
        else:
            # Fallback: используем строковое поле env
            env = component.get("env", "")
            if env:
                console.print(f"[bold white]ENV:[/bold white]")
                # ENV уже отформатирован как строка "KEY1=value1, KEY2=value2"
                env_pairs = [pair.strip() for pair in env.split(",")]
                for env_pair in env_pairs:
                    if "=" in env_pair:
                        key, value = env_pair.split("=", 1)
                        highlighted_value = Highlighter.highlight_value(value)
                        console.print(
                            f"[white]  [bold bright_white]{key}[/bold bright_white]: {highlighted_value}[/white]")

        # Тома
        volumes = component.get("_volumes", [])
        if volumes:
            console.print(f"[bold white]VOLUMES:[/bold white]")
            for volume in volumes:
                source = volume.get("source", "")
                target = volume.get("target", "")
                driver = volume.get("driver", "")
                if driver:
                    console.print(f"[white]  {source} -> {target} ({driver})[/white]")
                else:
                    console.print(f"[white]  {source} -> {target}[/white]")

        # Сетевые подключения
        networks = component.get("_networks", [])
        if networks:
            console.print(f"[bold white]NETWORKS:[/bold white]")
            for network in networks:
                name = network.get("name", "")
                driver = network.get("driver", "")
                subnet = network.get("subnet", "")
                if subnet:
                    console.print(f"  {name} ({driver}) - {subnet}")
                elif driver:
                    console.print(f"  {name} ({driver})")
                else:
                    console.print(f"  {name}")

        # Привязки
        binds = component.get("_binds", [])
        if binds:
            console.print(f"[bold white]BINDS:[/bold white]")
            for bind in binds:
                source = bind.get("source", "")
                target = bind.get("target", "")
                console.print(f"  {source} -> {target}")

        # Метки
        labels = component.get("_labels", [])
        if labels:
            console.print(f"[bold white]LABELS:[/bold white]")
            # labels может быть списком словарей или одним словарем
            if isinstance(labels, list):
                for label in labels:
                    for key, value in label.items():
                        console.print(f"[white]  {key}={value}[/white]")
            elif isinstance(labels, dict):
                for key, value in labels.items():
                    console.print(f"[white]  {key}={value}[/white]")

    except ImagenariumAPIError as e:
        console.print(f"Ошибка получения информации о компоненте: {e}")
        raise click.Abort()


@cli.command("tags")
@click.argument("name")
@click.option("--limit", "-l", type=int, help="Ограничить количество результатов")
@click.option("--no-cache", is_flag=True, help="Не использовать кеш")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def component_tags(
        ctx,
        name: str,
        limit: Optional[int],
        no_cache: bool,
        no_headers: bool,
        verbose: bool,
):
    """Показывает теги развертываний для компонента"""
    try:
        # Устанавливаем режим verbose для логирования
        set_verbose(verbose)

        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли
        show_console_header(api, show_header=not no_headers)

        # Используем сервис для получения данных в унифицированном формате
        svc = ComponentsService(api_client=api)

        # Используем callback для прогресс-бара (вызывается только при реальных запросах)
        from core.progress import create_progress_context

        with create_progress_context(
                "Получение информации о компонентах...",
        ) as progress_callback:
            component = svc.get(name, progress=progress_callback)

        if not component:
            console.print(f"Компонент '{name}' не найден")
            return

        # Извлекаем информацию о репозитории и образе (данные в snake_case)
        repo = component.get("repo", "")
        if not repo:
            console.print(
                f"[red]Не удалось получить информацию о репозитории для компонента {name}[/red]"
            )
            return

        # Получаем образ и тег (данные в snake_case)
        image_name = component.get("image", "")
        image_tag = component.get("tag", "")

        # Формируем image из TAG до __ включая __
        # ВАЖНО: API принимает формат ":<префикс_тега_до_двойного_подчеркивания_включая_его>"
        # Например: ":dev__" - это ПРАВИЛЬНЫЙ формат, НЕ МЕНЯТЬ!
        if "__" in image_tag:
            # Берем подстроку до __ включая __
            tag_part = image_tag.split("__")[0] + "__"
            # Используем только префикс тега с двоеточием
            search_image = f":{tag_part}"
        else:
            # Если нет __, используем полную версию тега
            tag_part = image_tag  # Для фильтрации
            search_image = f"{image_name}:{image_tag}"

        # Используем callback для прогресс-бара при получении тегов
        from core.progress import create_progress_context

        with create_progress_context(
                "Загрузка тегов развертываний...",
        ) as progress_callback:
            # Используем сервис для получения тегов
            tags = svc.get_deployment_tags(repo, search_image, no_cache, progress=progress_callback)

        if not tags:
            console.print(f"[yellow]Теги не найдены для {repo}/{search_image}[/yellow]")
            return

        # Фильтруем теги: исключаем тег, который точно соответствует поисковому запросу
        # Например, если ищем по ":dev__", то исключаем тег "dev__"
        filtered_tags = []
        for tag in tags:
            tag_name = tag["name"]
            # Если тег точно соответствует поисковому запросу (без дополнительной части), исключаем его
            if tag_name != tag_part:
                filtered_tags.append(tag)

        tags = filtered_tags

        if not tags:
            console.print(
                f"[yellow]Нет доступных тегов для {repo}/{search_image}[/yellow]"
            )
            return

        # Применяем лимит если указан
        if limit:
            tags = tags[:limit]

        # Подготавливаем данные для таблицы в стиле других list команд
        from utils.formatters import format_table, format_output

        data = []
        for tag in tags:
            data.append({"tag": tag["name"]})

        format_table(data, no_headers=no_headers)

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка API: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Неожиданная ошибка: {e}[/red]")
        raise click.Abort()


def _parse_component_tag(component_spec):
    """
    Парсит спецификацию компонента в формате 'component:tag' или 'component'

    Args:
        component_spec: Строка в формате 'component:tag' или 'component'

    Returns:
        tuple: (component_name, tag) где tag может быть None для 'latest'
    """
    if ":" in component_spec:
        component_name, tag = component_spec.rsplit(":", 1)
        return component_name.strip(), tag.strip()
    else:
        return component_spec.strip(), "latest"


def _load_upgrades_from_file(file_path):
    """
    Загружает список обновлений из файла в формате tab-separated

    Args:
        file_path: Путь к файлу

    Returns:
        list: Список кортежей (component_name, tag)
    """
    upgrades = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Пропускаем пустые строки и комментарии
                if not line or line.startswith("#"):
                    continue

                # Парсим tab-separated формат
                if "\t" in line:
                    parts = line.split("\t", 1)
                    if len(parts) == 2:
                        component_name = parts[0].strip()
                        tag = parts[1].strip()
                        upgrades.append((component_name, tag))
                    else:
                        console.print(
                            f"[yellow]Предупреждение: строка {line_num} в файле {file_path} имеет неверный формат[/yellow]"
                        )
                else:
                    console.print(
                        f"[yellow]Предупреждение: строка {line_num} в файле {file_path} не содержит табуляцию[/yellow]"
                    )

    except FileNotFoundError:
        console.print(f"[red]Файл {file_path} не найден[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Ошибка чтения файла {file_path}: {e}[/red]")
        raise click.Abort()

    return upgrades


def _extract_current_tag_from_component(component, svc: ComponentsService):
    """
    Извлекает текущий тег из компонента (из task, если доступен, иначе из component.image)

    Args:
        component: Словарь с информацией о компоненте
        svc: Сервис компонентов

    Returns:
        str: Текущий тег или 'latest' если не найден
    """
    try:
        # Сначала проверяем поле tag в унифицированном формате (snake_case)
        # Это поле уже содержит полный тег, если компонент получен через сервис
        if "tag" in component:
            tag = component.get("tag")
            if tag:
                return tag

        # Если нет поля tag, пытаемся извлечь из сырых данных
        # Используем методы сервиса для извлечения из task или image
        task_tag = svc.extract_tag_from_task(component)
        if task_tag:
            return task_tag
        return svc.extract_tag_from_component(component)
    except Exception:
        return "latest"


def _get_component_current_tag(api, component_name, no_cache=False):
    """
    Получает текущий тег компонента (из task, если доступен, иначе из component.image)

    Args:
        api: API клиент
        component_name: Имя компонента
        no_cache: Игнорировать кеш

    Returns:
        str: Текущий тег или None если компонент не найден
    """
    try:
        # Используем сервис для получения данных в унифицированном формате
        svc = ComponentsService(api_client=api)
        component = svc.get(component_name)
        if not component:
            return None
        # Возвращаем тег (данные в snake_case)
        tag = component.get("tag", "")
        return tag if tag else "latest"

    except Exception:
        return None


def _validate_tag_availability(api, component_name, target_tag, no_cache=False):
    """
    Проверяет доступность указанного тега в репозитории компонента

    Args:
        api: API клиент
        component_name: Имя компонента
        target_tag: Целевой тег для проверки
        no_cache: Не использовать кеш

    Returns:
        tuple: (is_available, error_message) где is_available - bool, error_message - str или None
    """
    try:
        # Используем сервис для получения данных в унифицированном формате
        svc = ComponentsService(api_client=api)
        component = svc.get(component_name)
        if not component:
            return False, "Компонент не найден"

        # Извлекаем информацию о репозитории и образе (данные в snake_case)
        repo = component.get("repo", "")
        if not repo:
            return False, "Репозиторий не найден"

        # Получаем образ и тег (данные в snake_case)
        image_name = component.get("image", "")
        image_tag = component.get("tag", "")
        if not image_tag:
            image_tag = "latest"

        # Для тегов с __ проверяем доступность через сервис
        if "__" in target_tag:
            # Формируем поисковый запрос по префиксу
            tag_part = target_tag.split("__")[0] + "__"
            search_image = f":{tag_part}"

            # Получаем список доступных тегов через сервис
            tags = svc.get_deployment_tags(repo, search_image, no_cache)
            if not tags:
                return False, f"Не удалось получить теги для {repo}/{search_image}"

            # Проверяем, есть ли целевой тег в списке
            available_tags = [tag["name"] for tag in tags]
            if target_tag not in available_tags:
                return False, f"Тег {target_tag} не найден в репозитории {repo}"

        # Для стабильных тегов (без __) считаем их всегда доступными
        # так как они не запрашиваются через API тегов

        return True, None

    except Exception as e:
        return False, f"Ошибка проверки тега: {str(e)}"


def _get_component_latest_tag(api, component_name, no_cache=False):
    """
    Получает последний доступный тег для компонента

    Args:
        api: API клиент
        component_name: Имя компонента

    Returns:
        str: Последний тег или None если не найден
    """
    try:
        # Используем сервис для получения данных в унифицированном формате
        svc = ComponentsService(api_client=api)
        component = svc.get(component_name)
        if not component:
            return None

        # Извлекаем информацию о репозитории и образе (данные в snake_case)
        repo = component.get("repo", "")
        if not repo:
            return None

        # Получаем образ и тег (данные в snake_case)
        image_name = component.get("image", "")
        image_tag = component.get("tag", "")
        if not image_tag:
            image_tag = "latest"

        # Формируем image из TAG до __ включая __
        # ВАЖНО: API принимает формат ":<префикс_тега_до_двойного_подчеркивания_включая_его>"
        # Например: ":dev__" - это ПРАВИЛЬНЫЙ формат, НЕ МЕНЯТЬ!
        if "__" in image_tag:
            tag_part = image_tag.split("__")[0] + "__"
            search_image = f":{tag_part}"
        else:
            # Для тегов без __ не запрашиваем список тегов - это стабильные версии
            return None

        # Получаем теги через сервис
        tags = svc.get_deployment_tags(repo, search_image, no_cache)

        if not tags:
            # Если теги не найдены, возвращаем None
            # Это означает, что компонент не может быть обновлен
            return None

        # Фильтруем теги: исключаем тег, который точно соответствует префиксу
        # Например, если ищем по ":dev__", то исключаем тег "dev__"
        filtered_tags = []
        for tag in tags:
            tag_name = tag["name"]
            if tag_name != tag_part:  # Исключаем префикс, а не полный тег
                filtered_tags.append(tag)

        if not filtered_tags:
            return None

        # Дополнительная проверка: если у компонента нет __ в теге,
        # но API возвращает теги с __, то это неправильный репозиторий
        if "__" not in image_tag and filtered_tags:
            # Проверяем, есть ли теги без __ в результате
            non_underscore_tags = [
                tag for tag in filtered_tags if "__" not in tag["name"]
            ]
            if not non_underscore_tags:
                # Если все теги содержат __, а у компонента нет, то это неправильный репозиторий
                return None
            # Используем только теги без __
            filtered_tags = non_underscore_tags

        # Возвращаем первый (самый новый) тег
        return filtered_tags[0]["name"]

    except Exception:
        return None


def _get_components_with_filters(api, filter_specs, no_cache=False):
    """
    Получает список компонентов с применением фильтров

    Args:
        api: API клиент
        filter_specs: Список спецификаций фильтров
        no_cache: Не использовать кеш

    Returns:
        Кортеж (upgrades, components_data) где:
        - upgrades: Список кортежей (component_name, tag)
        - components_data: Исходные данные компонентов
    """
    from rich.console import Console

    console = Console()

    # Используем ComponentsService для получения данных
    svc = ComponentsService(api_client=api)

    # Используем callback для прогресс-бара (вызывается только при реальных запросах)
    from core.progress import create_progress_context

    with create_progress_context(
            "Получение информации о компонентах...",
    ) as progress_callback:
        # Получаем компоненты через сервис (с фильтрами)
        components_list = svc.list(
            filters=list(filter_specs) if filter_specs else None,
            columns_spec=None,
            no_cache=no_cache,
            progress=progress_callback,
        )

        # Получаем исходные данные для components_data (используем тот же callback)
        deployments = api.get_components(no_cache=no_cache, progress=progress_callback)

    # Преобразуем в список кортежей (component_name, tag)
    upgrades = []
    for comp_data in components_list:
        name = comp_data.get("name", "")
        tag = comp_data.get("tag", "")
        if name:  # Пропускаем пустые имена
            upgrades.append((name, tag))

    return upgrades, deployments


def _validate_upgrade_plan(api, upgrades, no_cache=False, components_data=None, force=False):
    """
    Валидирует план обновления с оптимизацией запросов к API

    Args:
        api: API клиент
        force: Пропустить валидацию
        upgrades: Список кортежей (component_name, tag)
        no_cache: Не использовать кеш

    Returns:
        tuple: (valid_upgrades, invalid_upgrades)
    """
    valid_upgrades = []
    invalid_upgrades = []

    # Если force=True, пропускаем валидацию
    if force:
        verbose_print("Force mode: skipping validation")
        # Нужно получить components_index для формирования правильных данных
        if components_data is not None:
            all_deployments = components_data
        else:
            all_deployments = api.get_components(no_cache=no_cache)

        components_index = {}
        for group in all_deployments:
            stacks = group.get("stacks", [])
            for stack in stacks:
                stack_components = stack.get("components", [])
                for comp in stack_components:
                    comp_name = comp.get("name")
                    if comp_name:
                        result = comp.copy()
                        namespace = group.get("namespace")
                        stack_id = stack.get("stackId")
                        result["namespace"] = namespace
                        result["stack_id"] = f"{stack_id}@{namespace}"
                        components_index[comp_name] = result

        # Формируем valid_upgrades напрямую
        svc = ComponentsService(api_client=api)
        for component_name, target_tag in upgrades:
            if component_name in components_index:
                component_data = components_index[component_name]
                current_tag = _extract_current_tag_from_component(component_data, svc)
                component_namespace = component_data.get("namespace", "")
                valid_upgrades.append((component_name, target_tag, current_tag, component_namespace, component_data))

        verbose_print(f"Force mode: {len(valid_upgrades)} components prepared without validation")
        return valid_upgrades, []

    # Шаг 1: Получаем информацию о всех компонентах
    component_info = {}

    # Используем переданные данные или получаем их заново
    if components_data is not None:
        all_deployments = components_data
    else:
        all_deployments = api.get_components(no_cache=no_cache)

    # Создаем индекс компонентов по имени для быстрого поиска
    components_index = {}
    for group in all_deployments:
        stacks = group.get("stacks", [])
        for stack in stacks:
            stack_components = stack.get("components", [])
            for comp in stack_components:
                comp_name = comp.get("name")
                if comp_name:
                    # Добавляем дополнительную информацию о стеке и namespace
                    result = comp.copy()
                    namespace = group.get("namespace")
                    stack_id = stack.get("stackId")
                    result["namespace"] = namespace
                    result["stack_id"] = f"{stack_id}@{namespace}"
                    result["stack_version"] = stack.get("version")
                    result["stack_status"] = stack.get("status")
                    result["stack_repo"] = stack.get("repo")
                    result["stack_branch"] = stack.get("branch")
                    result["stack_commit"] = stack.get("commit")
                    result["stack_tag"] = stack.get("tag")
                    result["stack_timestamp"] = stack.get("timestamp")
                    components_index[comp_name] = result

    for component_name, target_tag in upgrades:
        # Ищем компонент в индексе (для получения сырых данных)
        component_raw = components_index.get(component_name)
        if not component_raw:
            invalid_upgrades.append((component_name, target_tag, "Компонент не найден"))
            continue

        # Получаем компонент через сервис для получения нормализованных данных с полным тегом
        svc = ComponentsService(api_client=api)
        component_normalized = svc.get(component_name, no_cache=no_cache)

        # Извлекаем текущий тег из нормализованных данных (содержат поле tag с полным тегом)
        if component_normalized and "tag" in component_normalized:
            current_tag = component_normalized.get("tag", "latest")
        else:
            # Fallback: извлекаем из сырых данных
            current_tag = _extract_current_tag_from_component(component_raw, svc)

        # Используем нормализованные данные если есть, иначе сырые
        component = component_normalized if component_normalized else component_raw

        component_info[component_name] = {
            "current_tag": current_tag,
            "target_tag": target_tag,
            "component": component,
        }

    # Шаг 2: Извлекаем уникальные пары repository + image для тегов с __
    unique_requests = set()
    component_requests = {}  # component_name -> (repository, image)

    for component_name, info in component_info.items():
        if info["target_tag"] != "latest":
            continue  # Пропускаем компоненты с конкретным тегом

        # Получаем информацию о компоненте для извлечения repository и image
        # Используем уже полученную информацию из component_info, если она есть
        component = info.get("component")
        if not component:
            # Используем сервис для получения данных в унифицированном формате
            svc = ComponentsService(api_client=api)
            component = svc.get(component_name)
            if not component:
                invalid_upgrades.append(
                    (component_name, info["target_tag"], "Компонент не найден")
                )
                continue

        # Получаем repo (данные в snake_case или сырые данные для обратной совместимости)
        repo = component.get("repo", "") if isinstance(component, dict) else component.get("repo", "")
        if not repo:
            invalid_upgrades.append(
                (component_name, info["target_tag"], "Репозиторий не найден")
            )
            continue

        # Получаем образ и тег (данные в snake_case или сырые данные для обратной совместимости)
        image_name = component.get("image", "") if isinstance(component, dict) else component.get("image", "")
        image_tag = component.get("tag", "") if isinstance(component, dict) else component.get("tag", "latest")
        if not image_tag:
            image_tag = "latest"

        # Проверяем, есть ли __ в теге
        if "__" in image_tag:
            tag_part = image_tag.split("__")[0] + "__"
            search_image = f":{tag_part}"
            unique_requests.add((repo, search_image))
            component_requests[component_name] = (repo, search_image)
        else:
            # Для тегов без __ не запрашиваем теги
            invalid_upgrades.append(
                (
                    component_name,
                    info["current_tag"],
                    "Стабильная версия - обновление недоступно",
                )
            )

    # Шаг 3: Получаем теги для каждой уникальной пары
    tags_cache = {}  # (repository, image) -> list of tags

    if unique_requests:
        from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
        from rich.console import Console

        console = Console()

        # Используем сервис для получения тегов
        svc = ComponentsService(api_client=api)

        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console,
        ) as progress:
            task = progress.add_task("Получение актуальных тегов...", total=None)

            for i, (repo, search_image) in enumerate(unique_requests, 1):
                # Формируем понятное описание для пользователя
                display_image = search_image.replace(":", "").replace(
                    "_", " "
                )  # Убираем двоеточие и подчеркивания для отображения
                display_repo = repo.replace(
                    "_", " "
                )  # Убираем подчеркивания для отображения
                progress.update(
                    task,
                    description=f"Получение актуального тега для {display_repo}/{display_image} ({i}/{len(unique_requests)})",
                )

                # Небольшая задержка для видимости прогресса
                import time

                time.sleep(0.1)

                # Создаем callback, который обновляет общий прогресс
                # Callback от сервиса будет вызван только при реальных запросах
                from core.progress import RichProgressCallback
                step_info = f"{i}/{len(unique_requests)}"
                progress_callback = RichProgressCallback(console, progress, task, step_info=step_info)

                # Используем сервис с callback (callback вызовется автоматически при реальном запросе)
                tags = svc.get_deployment_tags(repo, search_image, no_cache=no_cache, progress=progress_callback)
                tags_cache[(repo, search_image)] = tags

    # Шаг 4: Применяем результаты к компонентам
    for component_name, info in component_info.items():
        if info["target_tag"] != "latest":
            # Для компонентов с конкретным тегом проверяем доступность тега
            if info["current_tag"] != info["target_tag"]:
                # Проверяем доступность целевого тега в репозитории
                is_available, error_msg = _validate_tag_availability(
                    api, component_name, info["target_tag"], no_cache
                )
                if is_available:
                    # Получаем namespace из информации о компоненте
                    component_namespace = info["component"].get("namespace", "")
                    valid_upgrades.append(
                        (
                            component_name,
                            info["target_tag"],
                            info["current_tag"],
                            component_namespace,
                            info["component"],
                        )
                    )
                else:
                    invalid_upgrades.append(
                        (component_name, info["target_tag"], error_msg)
                    )
            continue

        if component_name not in component_requests:
            continue  # Уже обработан выше

        repo, search_image = component_requests[component_name]
        tags = tags_cache.get((repo, search_image), [])

        if not tags:
            invalid_upgrades.append(
                (
                    component_name,
                    info["current_tag"],
                    "Не удалось получить последний тег",
                )
            )
            continue

        # Ищем последний тег (исключая префикс)
        current_tag = info["current_tag"]
        latest_tag = None

        # Определяем префикс для исключения
        if "__" in current_tag:
            tag_part = current_tag.split("__")[0] + "__"
        else:
            tag_part = current_tag

        for tag in tags:
            tag_name = tag.get("name", tag.get("tag", ""))
            if tag_name != tag_part:  # Исключаем префикс, а не полный тег
                latest_tag = tag_name
                break

        if latest_tag is None:
            invalid_upgrades.append(
                (component_name, info["current_tag"], "Нет доступных обновлений")
            )
            continue

        # Проверяем, что теги разные
        if current_tag == latest_tag:
            continue

        # Получаем namespace из информации о компоненте
        component_namespace = info["component"].get("namespace", "")
        valid_upgrades.append(
            (
                component_name,
                latest_tag,
                current_tag,
                component_namespace,
                info["component"],
            )
        )

    return valid_upgrades, invalid_upgrades


@cli.command("upgrade")
@click.argument("components", nargs=-1, metavar="[COMPONENT:TAG]...", required=False)
@click.option(
    "--from-file",
    "upgrade_file",
    help="Загрузить список обновлений из файла (tab-separated)",
)
@click.option(
    "--check", is_flag=True, help="Показать доступные обновления без выполнения"
)
@click.option("--dry-run", is_flag=True, help="Предварительный просмотр без выполнения")
@click.option("--all", is_flag=True, help="Обновить все компоненты до последних тегов")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.option(
    "--filter",
    "filter_spec",
    multiple=True,
    help="Фильтр компонентов. Формат: COLUMN=value",
)
@click.option(
    "--to-tag",
    help="Обновить все отфильтрованные компоненты до указанного тега (с проверкой доступности)",
)
@click.option(
    "--confirm", is_flag=True, help="Подтвердить обновления без интерактивного запроса"
)
@click.option("--force", is_flag=True, help="Принудительное обновление без проверки доступности тега")
@click.option("--no-cache", is_flag=True, help="Не использовать кеш при проверке тегов")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option(
    "--export-current", is_flag=True, help="Экспортировать текущие версии в stdout"
)
@click.option(
    "--export-latest", is_flag=True, help="Экспортировать последние версии в stdout"
)
@click.option(
    "--export-upgradable",
    is_flag=True,
    help="Экспортировать компоненты для обновления в stdout",
)
@click.pass_context
def upgrade_components(
        ctx,
        components,
        upgrade_file,
        check,
        dry_run,
        all,
        filter_spec,
        to_tag,
        confirm,
        force,
        no_cache,
        no_headers,
        export_current,
        export_latest,
        export_upgradable,
        verbose,
):
    """Обновляет компоненты до указанных тегов

    Примеры:
      imgctl components upgrade web-api-staging                    # Обновить до последнего тега
      imgctl components upgrade web-api-staging:v1.2.3            # Обновить до конкретного тега
      imgctl components upgrade web-api-staging db-staging:latest # Несколько компонентов
      imgctl components upgrade --from-file upgrades.txt          # Из файла
      imgctl components upgrade --all                             # Все компоненты
      imgctl components upgrade --filter NAME~^oms-api- --to-tag dev__2025_01_15_10_00-abc123  # Обновить все oms-api компоненты до указанного тега
      imgctl components upgrade --filter NAMESPACE=staging --to-tag latest  # Обновить все компоненты в namespace staging
      imgctl components upgrade --filter STATUS=RUNNING --to-tag dev__2025_01_15_10_00-abc123  # Обновить все запущенные компоненты
      imgctl components upgrade --check                           # Показать доступные обновления
      imgctl components upgrade --dry-run                         # Предварительный просмотр без выполнения
    """
    try:
        # Устанавливаем режим verbose для логирования
        set_verbose(verbose)

        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли
        show_console_header(api, show_header=not no_headers)

        # Обработка режимов экспорта
        if export_current or export_latest or export_upgradable:
            # Определяем список компонентов для экспорта
            components_list = []

            if components:
                # Если указаны компоненты в аргументах, используем их
                for component_spec in components:
                    component_name, _ = _parse_component_tag(component_spec)
                    # Получаем текущий тег через сервис
                    svc = ComponentsService(api_client=api)
                    component = svc.get(component_name, no_cache=no_cache)
                    if component:
                        current_tag = component.get("tag", "latest")
                        components_list.append((component_name, current_tag))
            elif filter_spec:
                # Если есть фильтры, используем их
                components_list, _ = _get_components_with_filters(
                    api, list(filter_spec), no_cache
                )
            else:
                # Иначе используем все компоненты
                components_list, _ = _get_components_with_filters(
                    api, None, no_cache
                )

            if export_current:
                # Экспортируем текущие версии
                for component_name, current_tag in components_list:
                    print(f"{component_name}\t{current_tag}")
                return

            elif export_latest:
                # Экспортируем последние версии
                for component_name, _ in components_list:
                    latest_tag = _get_component_latest_tag(
                        api, component_name, no_cache
                    )
                    if latest_tag:
                        print(f"{component_name}\t{latest_tag}")
                    else:
                        print(f"{component_name}\t")
                return

            elif export_upgradable:
                # Экспортируем компоненты для обновления
                # Формируем список upgrades для валидации с прогресс-баром
                upgrades_for_validation = [(name, "latest") for name, _ in components_list]

                # Валидируем план обновления (это покажет прогресс)
                valid_upgrades, invalid_upgrades = _validate_upgrade_plan(
                    api, upgrades_for_validation, no_cache, None, force
                )

                # Экспортируем валидные обновления
                for component_name, latest_tag, current_tag, _, _ in valid_upgrades:
                    print(f"{component_name}\t{latest_tag}")
                return

        # Определяем список обновлений
        upgrades = []

        if upgrade_file:
            # Загружаем из файла
            console.print(
                f"[blue]Загрузка обновлений из файла {upgrade_file}...[/blue]"
            )
            upgrades = _load_upgrades_from_file(upgrade_file)
        elif all or (not components and not filter_spec and not upgrade_file):
            # Получаем все компоненты без фильтров
            upgrades, components_data = _get_components_with_filters(
                api, None, no_cache
            )

            # Заменяем теги на 'latest' для обновления до последних версий
            upgrades = [(name, "latest") for name, _ in upgrades]
        elif filter_spec:
            # Получаем компоненты с применением фильтров (используем TTL кеша)
            upgrades, components_data = _get_components_with_filters(
                api, list(filter_spec), no_cache
            )

            if to_tag:
                # Обновляем все отфильтрованные компоненты до указанного тега

                # Пропускаем валидацию если используется --force
                if force:
                    console.print("[yellow]Флаг --force активен: проверка доступности тегов пропущена[/yellow]")
                    upgrades = [(name, to_tag) for name, _ in upgrades]
                    verbose_print(f"Force mode: {len(upgrades)} components will be upgraded without validation")
                else:
                    # Проверяем доступность тега для каждого компонента с прогресс-баром
                    original_count = len(upgrades)
                    validated_upgrades = []

                    with Progress(
                            SpinnerColumn(),
                            TextColumn("[progress.description]{task.description}"),
                            console=console,
                    ) as progress:
                        task = progress.add_task(
                            f"Проверка доступности тега '{to_tag}' для {original_count} компонентов...",
                            total=original_count
                        )

                        for name, _ in upgrades:
                            is_available, error_msg = _validate_tag_availability(
                                api, name, to_tag, no_cache
                            )
                            if is_available:
                                validated_upgrades.append((name, to_tag))
                            else:
                                console.print(f"[yellow]Пропуск {name}: {error_msg}[/yellow]")
                            progress.advance(task)

                    upgrades = validated_upgrades

                    if len(validated_upgrades) < original_count:
                        console.print(
                            f"[blue]Валидных обновлений: {len(validated_upgrades)} из {original_count}[/blue]"
                        )
            else:
                # Заменяем теги на 'latest' для обновления до последних версий
                upgrades = [(name, "latest") for name, _ in upgrades]
        elif components:
            # Парсим аргументы командной строки (используем TTL кеша)
            for component_spec in components:
                component_name, tag = _parse_component_tag(component_spec)
                upgrades.append((component_name, tag))

            # Получаем данные компонентов для валидации
            _, components_data = _get_components_with_filters(api, None, no_cache)

        if not upgrades:
            console.print("[yellow]Нет компонентов для обновления[/yellow]")
            return

        # Валидируем план обновления
        valid_upgrades, invalid_upgrades = _validate_upgrade_plan(
            api, upgrades, no_cache, components_data, force
        )

        # Показываем невалидные обновления
        if invalid_upgrades:
            console.print("[red]Найдены ошибки в плане обновления:[/red]")
            for component_name, target_tag, error in invalid_upgrades:
                # Определяем namespace для подсветки
                component_namespace = None
                if components_data:
                    for group in components_data:
                        for stack in group.get("stacks", []):
                            for comp in stack.get("components", []):
                                if comp.get("name") == component_name:
                                    component_namespace = group.get("namespace", "")
                                    break

                from utils.highlighter import Highlighter
                highlighted_name = (
                    Highlighter.highlight_component_name(component_name, component_namespace)
                    if component_namespace
                    else component_name
                )
                highlighted_tag = Highlighter.highlight_tag(target_tag)
                console.print(f"  ❌ {highlighted_name}:{highlighted_tag} - {error}")
            console.print()

        if not valid_upgrades:
            console.print("[red]Нет валидных обновлений для выполнения[/red]")
            return

        # Показываем план обновления
        console.print(
            f"[green]План обновления ({len(valid_upgrades)} компонентов):[/green]"
        )
        for (
                component_name,
                target_tag,
                current_tag,
                component_namespace,
                component_data,
        ) in valid_upgrades:
            if current_tag == target_tag:
                # Создаем Text объект для правильной раскраски
                from rich.text import Text

                text = Text()
                text.append("  ")

                # Подсвечиваем имя компонента
                if "-" in component_name and component_namespace:
                    namespace_suffix = f"-{component_namespace}"
                    if component_name.endswith(namespace_suffix):
                        component_part = component_name[: -len(namespace_suffix)]
                        text.append(component_part)
                        text.append(namespace_suffix, style="dim")
                    else:
                        text.append(component_name)
                else:
                    text.append(component_name)

                text.append(": ")
                text.append("уже актуален", style="green")
                console.print(text)
            else:
                from rich.text import Text

                text = Text()
                text.append("  ")

                # Подсвечиваем имя компонента
                if "-" in component_name and component_namespace:
                    namespace_suffix = f"-{component_namespace}"
                    if component_name.endswith(namespace_suffix):
                        component_part = component_name[: -len(namespace_suffix)]
                        text.append(component_part)
                        text.append(namespace_suffix, style="dim")
                    else:
                        text.append(component_name)
                else:
                    text.append(component_name)

                text.append(": ")
                text.append(current_tag, style="yellow")
                text.append(" → ")
                text.append(target_tag, style="green")
                console.print(text)

        # Если это режим проверки или dry-run, выходим
        if check or dry_run:
            if check:
                console.print(
                    "\n[blue]Режим проверки - обновления не выполняются[/blue]"
                )
            else:
                console.print(
                    "\n[blue]Dry-run режим - обновления не выполняются[/blue]"
                )
            return

        # Подтверждение
        if not confirm:
            if not click.confirm(
                    f"\nВыполнить обновление {len(valid_upgrades)} компонентов?"
            ):
                console.print("[yellow]Обновление отменено[/yellow]")
                return

        # Выполняем обновления с прогресс-барами
        console.print(f"\n[green]Выполнение обновлений...[/green]")
        success_count = 0
        error_count = 0

        # Выполняем обновления с прогресс-барами
        with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TimeElapsedColumn(),
                console=console,
                transient=False,
        ) as progress:

            for (
                    component_name,
                    target_tag,
                    current_tag,
                    component_namespace,
                    component_data,
            ) in valid_upgrades:
                # DEBUG: выводим информацию о всех компонентах для обновления
                verbose_print(f"Component: {component_name}, current: {current_tag}, target: {target_tag}")

                # С --force пропускаем проверку "уже актуален"
                if current_tag == target_tag and not force:
                    verbose_print(f"  Skipping {component_name} - already up to date")
                    continue  # Пропускаем уже актуальные (если не force)

                from utils.highlighter import Highlighter
                highlighted_name = Highlighter.highlight_component_name(
                    component_name, component_namespace
                )

                # Создаем описание для прогресса с подсветкой тегов
                description = f"{highlighted_name}: [yellow]{current_tag}[/yellow] → [green]{target_tag}[/green]"

                # Создаем задачу с анимацией и временем
                task_id = progress.add_task(description, total=100)

                try:
                    # Используем уже полученные данные о компоненте
                    component = component_data

                    # Получаем образ и тег (данные в snake_case или сырые данные для обратной совместимости)
                    # component_data из сервиса в snake_case, из старого кода может быть в сыром формате
                    image_name = component.get("image", "")
                    if not image_name:
                        # Если нет в snake_case, извлекаем из сырых данных (для обратной совместимости)
                        image = component.get("image", "")
                        child_container = component.get("childContainer")
                        if child_container and child_container.get("image"):
                            image = child_container.get("image")
                        # Извлекаем имя образа без тега
                        if ":" in image:
                            image_name, _ = image.rsplit(":", 1)
                        else:
                            image_name = image
                    # image в snake_case уже без тега

                    # Формируем новый образ с целевым тегом
                    new_image = f"{image_name}:{target_tag}"

                    # Выполняем обновление
                    # Извлекаем stack (данные в snake_case или сырые данные для обратной совместимости)
                    stack = component.get("stack", "")
                    if stack:
                        stack_name = stack.split("@")[0] if "@" in stack else stack
                    else:
                        # Пробуем получить из сырых данных для обратной совместимости
                        stack_id = component.get("stack_id", "")
                        stack_name = stack_id.split("@")[0] if "@" in stack_id and stack_id else ""

                    verbose_print(f"Upgrading {component_name}: {current_tag} -> {target_tag}")
                    verbose_print(f"  namespace: {component_namespace}, stack: {stack_name}")
                    verbose_print(f"  new image: {new_image}")

                    svc = ComponentsService(api_client=api)
                    svc.update(
                        component_name, new_image, component_namespace, stack_name, component_data
                    )

                    # Завершаем прогресс
                    progress.update(task_id, advance=100)
                    progress.remove_task(task_id)

                    success_count += 1

                except Exception as e:
                    # Завершаем прогресс
                    progress.update(task_id, advance=100)
                    progress.remove_task(task_id)

                    error_count += 1
                    # Выводим сообщение об ошибке
                    console.print(
                        f"❌ {highlighted_name}: [yellow]{current_tag}[/yellow] → [green]{target_tag}[/green]: {str(e)[:50]}..."
                    )
                    continue

                # Выводим финальное сообщение об успехе
                console.print(
                    f"✅ {highlighted_name}: [yellow]{current_tag}[/yellow] → [green]{target_tag}[/green]"
                )

        # Выводим итоговую статистику
        if success_count > 0 or error_count > 0:
            console.print()
            if success_count > 0:
                console.print(
                    f"[green]Успешно обновлено: {success_count} компонентов[/green]"
                )
            if error_count > 0:
                console.print(
                    f"[red]Ошибок обновления: {error_count} компонентов[/red]"
                )

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка API: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Неожиданная ошибка: {e}[/red]")
        raise click.Abort()
