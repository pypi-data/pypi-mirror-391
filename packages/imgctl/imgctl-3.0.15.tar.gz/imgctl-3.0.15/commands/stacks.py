"""
Команды для управления стеками
"""

import click
from rich.console import Console

from core.api_client import ImagenariumAPIError
from core.services.stacks_service import StacksService
from utils.formatters import format_table, format_output, show_console_header

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
    """Управление стеками приложений"""
    pass


@cli.command("list")
@click.option(
    "--columns",
    help='Столбцы для отображения. Форматы: "NAME,STATUS" или "+COMPONENTS,-TIME". Доступные: NAME, NAMESPACE, VERSION, STATUS, REPO, COMMIT, TIME, TAG, PARAMS, COMPONENTS, PARAMS.<параметр>',
)
@click.option(
    "--filter",
    multiple=True,
    help="Фильтрация данных. Формат: COLUMN=value, COLUMN!=value, COLUMN~pattern. Примеры: STATUS=deployed, NAMESPACE!=test, NAME~postgres, PARAMS~database, PARAMS.DB_HOST=localhost",
)
@click.option("--limit", "-l", type=int, help="Ограничить количество записей")
@click.option("--no-cache", is_flag=True, help="Отключить кэширование")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option(
    "--output",
    "-o",
    help='Формат вывода данных: json, yaml, tsv, или template (например: "{NAME} - {STATUS}")',
)
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def list_stacks(ctx, columns, filter, limit, no_cache, no_headers, output, verbose):
    """Показывает список стеков

    По умолчанию: NAME, NAMESPACE, VERSION, STATUS. Дополнительные: REPO, COMMIT, TIME, TAG, PARAMS, COMPONENTS, PARAMS.<параметр>
    """
    try:
        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли (скрываем при --no-headers или --output)
        show_console_header(api, show_header=not (no_headers or output))

        # Сервис стеков
        svc = StacksService(api_client=api)

        # Используем callback для прогресс-бара (вызывается только при реальных запросах)
        from core.progress import create_progress_context

        with create_progress_context(
                "Получение списка стеков...",
        ) as progress_callback:
            # columns_spec передается в list, где он парсится и применяется
            rows = svc.list(
                filters=list(filter) if filter else None,
                columns_spec=columns,
                no_cache=no_cache,
                progress=progress_callback,
            )
        if not rows:
            console.print("[yellow]Стеки не найдены[/yellow]")
            return

        if limit:
            rows = rows[:limit]

        # Определяем столбцы для вывода (данные уже отфильтрованы в list)
        from utils.formatters import parse_filters

        # Если columns указан, используем столбцы из данных, иначе default
        if columns and rows:
            columns_to_show = list(rows[0].keys()) if rows else svc.get_default_columns()
        else:
            columns_to_show = svc.get_default_columns()

        # Данные уже отфильтрованы по столбцам в list
        data = rows

        if not output or output == "table":
            highlight_filters = parse_filters(list(filter)) if filter else None
            # Подсветку имен стеков делаем в format_table
            format_table(
                data,
                columns=columns_to_show,
                no_headers=no_headers,
                highlight_filters=highlight_filters,
            )
        else:
            format_output(data, output, columns=columns_to_show)

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка получения списка стеков: {e}[/red]")
        raise click.Abort()


@cli.command("get")
@click.argument("stack_id")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def get_stack(ctx, stack_id, verbose):
    """Показывает детальную информацию о стеке"""
    try:
        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли
        show_console_header(api)

        # Используем сервис для получения данных в унифицированном формате
        svc = StacksService(api_client=api)

        # Используем callback для прогресс-бара (вызывается только при реальных запросах)
        from core.progress import create_progress_context

        with create_progress_context(
                "Загрузка информации о стеке...",
        ) as progress_callback:
            stack = svc.get(stack_id, progress=progress_callback)

        if not stack:
            console.print(f"[red]Стек '{stack_id}' не найден[/red]")
            return

        # Выводим основную информацию (стек в snake_case формате)
        name = stack.get("name", "")
        if "@" in name:
            stack_name, namespace = name.split("@", 1)
            console.print(
                f"[bold white]NAME:[/bold white] {stack_name}[dim]@{namespace}[/dim]"
            )
        else:
            console.print(f"[bold white]NAME:[/bold white] {name}")
        namespace = stack.get("namespace", "")
        if namespace:
            console.print(f"[bold white]NAMESPACE:[/bold white] {namespace}")
        version = stack.get("version", "")
        if version:
            console.print(f"[bold white]VERSION:[/bold white] {version}")

        # Раскрашиваем статус
        from utils.highlighter import Highlighter

        status = stack.get("status", "UNKNOWN")
        styled_status = Highlighter.highlight(status, check_partial=True)
        console.print(f"[bold white]STATUS:[/bold white] {styled_status}")

        from utils.formatters import print_field

        print_field(stack, "repo")
        print_field(stack, "commit")
        # Преобразуем timestamp в нормальный вид
        timestamp = stack.get("time", "")
        if timestamp:
            try:
                from datetime import datetime
                dt = datetime.fromtimestamp(int(timestamp))
                time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
                console.print(f"[bold white]TIME:[/bold white] {time_str}")
            except (ValueError, TypeError):
                console.print(f"[bold white]TIME:[/bold white] {timestamp}")
        tag = stack.get("tag", "")
        if tag:
            console.print(f"[bold white]TAG:[/bold white] {tag}")

        # Параметры: показываем динамические params.* столбцы, если они есть
        # Иначе используем поле params как fallback
        param_keys = [k for k in stack.keys() if k.startswith("params.") and not k.endswith("_raw")]
        if param_keys:
            console.print(f"[bold white]PARAMS:[/bold white]")
            for key in sorted(param_keys):
                value = stack.get(key, "")
                param_name = key.replace("params.", "")
                formatted_value = Highlighter.highlight_value(value)
                console.print(
                    f"[white]  [bold bright_white]{param_name}[/bold bright_white]: {formatted_value}[/white]")
        else:
            # Fallback: используем строковое поле params, если нет динамических полей
            params = stack.get("params", "")
            if params:
                console.print(f"[bold white]PARAMS:[/bold white]")
                for pair in params.split(", "):
                    if "=" in pair:
                        key, value = pair.split("=", 1)
                        # Попытка определить тип значения из строки
                        typed_value = _parse_string_value(value)
                        formatted_value = Highlighter.highlight_value(typed_value)
                        console.print(
                            f"[white]  [bold bright_white]{key}[/bold bright_white]: {formatted_value}[/white]")
            else:
                console.print(f"[bold white]PARAMS:[/bold white] [dim]Нет[/dim]")

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка получения информации о стеке: {e}[/red]")
        raise click.Abort()


# @cli.command("deploy")
# @click.argument("namespace")
# @click.argument("stack_id")
# @click.argument("version")
# @click.option("--repository", required=True, help="Git репозиторий")
# @click.option("--git-ref", required=True, help="Git ref (ветка или тег)")
# @click.option("--param", multiple=True, help="Параметр деплоя (формат: key=value)")
# @click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
# @click.pass_context
# def deploy_stack(
#     ctx, namespace, stack_id, version, repository, git_ref, param, verbose
# ):
#     """Деплоит стек в namespace"""
#     try:
#         # Создаем API клиент с нужными параметрами
#         api = _get_api_client(verbose=verbose, ctx=ctx)

#         # Собираем параметры деплоя
#         params = {}
#         for p in param:
#             if "=" in p:
#                 key, value = p.split("=", 1)
#                 params[key] = value
#             else:
#                 console.print(f"[yellow]Пропускаем неправильный параметр: {p}[/yellow]")

#         console.print(
#             f"[blue]Деплой стека {stack_id} версии {version} в namespace {namespace}...[/blue]"
#         )
#         api.deploy_stack(namespace, stack_id, version, repository, git_ref, params)
#         console.print(f"[green]Стек {stack_id} успешно задеплоен[/green]")

#     except ImagenariumAPIError as e:
#         console.print(f"[red]Ошибка деплоя стека: {e}[/red]")
#         raise click.Abort()


# @cli.command("undeploy")
# @click.argument("namespace")
# @click.argument("stack_id")
# @click.argument("version")
# @click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
# @click.pass_context
# def undeploy_stack(ctx, namespace, stack_id, version, verbose):
#     """Андеплоит стек из namespace"""
#     try:
#         # Создаем API клиент с нужными параметрами
#         api = _get_api_client(verbose=verbose, ctx=ctx)

#         console.print(
#             f"[blue]Андеплой стека {stack_id} версии {version} из namespace {namespace}...[/blue]"
#         )
#         result = api.undeploy_stack(namespace, stack_id, version)
#         console.print(f"[green]Стек {stack_id} успешно андеплоен[/green]")

#         if result:
#             console.print(f"Результат: {result}")

#     except ImagenariumAPIError as e:
#         console.print(f"[red]Ошибка андеплоя стека: {e}[/red]")
#         raise click.Abort()


def _parse_stack_spec(stack_spec: str, commit: str = None):
    """
    Парсит спецификацию стека в новом формате

    Поддерживаемые форматы:
    1) <stackId>@<namespace> - берем текущий repo, commit, stackId, namespace
    2) <stackId>@<namespace>:<тег> - берем текущий repo, stackId, namespace, commit из тега
    3) <stackId>@<namespace> <commit> - берем текущий repo, stackId, namespace, commit из параметров

    Args:
        stack_spec: Спецификация стека
        commit: Дополнительный параметр commit (для формата 3)

    Returns:
        tuple: (stack_id, namespace, version, git_ref, repo_name)
    """
    # Формат 2: <stackId>@<namespace>:<тег>
    if ":" in stack_spec and "@" in stack_spec:
        # Находим последнее двоеточие (тег может содержать двоеточия)
        colon_pos = stack_spec.rfind(":")
        stack_part = stack_spec[:colon_pos]
        tag_part = stack_spec[colon_pos + 1:]

        if "@" in stack_part:
            stack_id, namespace = stack_part.split("@", 1)
            # Извлекаем commit из тега (например, dev__2025_08_05_10_17-6ca3d9f -> 6ca3d9f)
            if "__" in tag_part and "-" in tag_part:
                # Формат: dev__2025_08_05_10_17-6ca3d9f
                commit_from_tag = tag_part.split("-")[-1]
            else:
                # Если формат неожиданный, используем весь тег как commit
                commit_from_tag = tag_part

            return stack_id, namespace, None, commit_from_tag, None

    # Формат 1 и 3: <stackId>@<namespace> [commit]
    if "@" in stack_spec:
        stack_id, namespace = stack_spec.split("@", 1)
        return stack_id, namespace, None, commit, None

    # Fallback: старая логика
    return stack_spec, None, None, commit, None


def _get_stack_info_from_components(
        api,
        stack_id: str,
        namespace: str,
        no_cache: bool = False,
        progress=None,
):
    """
    Получает информацию о стеке из компонентов

    Args:
        api: API клиент
        stack_id: ID стека
        namespace: Namespace
        no_cache: Не использовать кэш
        progress: Callback для отображения прогресса

    Returns:
        dict: Информация о стеке или None
    """
    try:
        components = api.get_components(no_cache=no_cache, progress=progress)

        for group in components:
            group_namespace = group.get("namespace", "")
            if group_namespace != namespace:
                continue

            stacks = group.get("stacks", [])
            for stack in stacks:
                if stack.get("stackId") == stack_id:
                    return stack

        return None
    except Exception:
        return None


@cli.command("template")
@click.argument("stack_spec", metavar="STACK_SPEC")
@click.argument("commit", required=False, metavar="[COMMIT]")
@click.option(
    "--diff", is_flag=True, help="Показать diff между текущим commit и указанным COMMIT"
)
@click.option("--no-cache", is_flag=True, help="Отключить кэширование")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def get_template(ctx, stack_spec, commit, diff, no_cache, no_headers, verbose):
    """Получает и отображает шаблон деплоя для указанного стека.

    Поддерживает три формата спецификации стека:

    \b
    ФОРМАТ 1: STACK_ID@NAMESPACE
        Получает шаблон для текущего состояния стека.
        Автоматически извлекает репозиторий и commit из развернутого стека.

    \b
    ФОРМАТ 2: STACK_ID@NAMESPACE:TAG
        Получает шаблон для указанного тега.
        Commit извлекается из тега (например, dev__2025_08_05_10_17-6ca3d9f → 6ca3d9f).

    \b
    ФОРМАТ 3: STACK_ID@NAMESPACE COMMIT
        Получает шаблон для указанного commit.
        Позволяет явно указать конкретный commit для получения шаблона.

    \b
    РЕЖИМ DIFF:
        При указании --diff сравнивает текущий шаблон с шаблоном для указанного COMMIT.
        Показывает "Шаблоны не различаются" если они одинаковые, иначе выводит оба шаблона.
        Требует обязательного указания COMMIT.

    \b
    ПАРАМЕТРЫ:
        STACK_SPEC    Спецификация стека в одном из поддерживаемых форматов
        COMMIT        Git commit hash (только для формата 3)
    """
    try:
        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли
        show_console_header(api, show_header=not no_headers)

        # Парсим спецификацию стека
        stack_id, namespace, version, git_ref, repo_name = _parse_stack_spec(
            stack_spec, commit
        )

        if not stack_id or not namespace:
            console.print(
                f"[red]Неверный формат спецификации стека: {stack_spec}[/red]"
            )
            console.print("Поддерживаемые форматы:")
            console.print("  <stackId>@<namespace>")
            console.print("  <stackId>@<namespace>:<тег>")
            console.print("  <stackId>@<namespace> <commit>")
            raise click.Abort()

        # Используем callback для прогресс-бара
        from core.progress import create_progress_context

        with create_progress_context(
                "Получение информации о шаблоне стека...",
        ) as progress_callback:
            # Получаем информацию о стеке из компонентов
            stack_info = _get_stack_info_from_components(
                api, stack_id, namespace, no_cache, progress=progress_callback
            )

        if not stack_info:
            console.print(f"[red]Стек {stack_id}@{namespace} не найден[/red]")
            raise click.Abort()

        # Извлекаем необходимые параметры
        repo_name = stack_info.get("repo")
        if not repo_name:
            console.print(
                f"[red]Не удалось получить репозиторий для стека {stack_id}@{namespace}[/red]"
            )
            raise click.Abort()

        version = stack_info.get("version", "latest")

        # Если git_ref не указан, берем текущий commit из стека
        if not git_ref:
            git_ref = stack_info.get("commit")
            if not git_ref:
                console.print(
                    f"[red]Не удалось получить commit для стека {stack_id}@{namespace}[/red]"
                )
                raise click.Abort()

        # Проверяем, нужен ли режим diff
        if diff:
            # Режим diff - сравниваем шаблоны
            if not commit:
                console.print(f"[red]Для режима --diff необходимо указать COMMIT[/red]")
                raise click.Abort()

            # Используем callback для прогресс-бара
            from core.progress import create_progress_context

            with create_progress_context(
                    "Получение diff шаблонов...",
            ) as progress_callback:
                # Получаем diff
                diff_result = api.diff_template(
                    namespace, stack_id, version, commit, progress=progress_callback
                )

            # Выводим основную информацию в стиле других команд get (только если не --no-headers)
            if not no_headers:
                console.print(
                    f"[bold white]NAME:[/bold white] {stack_id}[dim]@{namespace}[/dim]"
                )
                console.print(f"[bold white]NAMESPACE:[/bold white] {namespace}")
                console.print(f"[bold white]VERSION:[/bold white] {version}")
                console.print(f"[bold white]REPO:[/bold white] {repo_name}")
                console.print(f"[bold white]CURRENT_COMMIT:[/bold white] {git_ref}")
                console.print(f"[bold white]DIFF_COMMIT:[/bold white] {commit}")
                console.print()

            # Проверяем, различаются ли шаблоны
            if diff_result.get("equals", False):
                console.print("[green]Шаблоны не различаются[/green]")
            else:
                console.print("[yellow]Шаблоны различаются:[/yellow]")
                console.print()
                console.print("[bold]Текущий шаблон:[/bold]")
                console.print(diff_result.get("oldTemplate", ""))
                console.print()
                console.print("[bold]Новый шаблон:[/bold]")
                console.print(diff_result.get("newTemplate", ""))
        else:
            # Обычный режим - получаем шаблон
            # Используем callback для прогресс-бара
            from core.progress import create_progress_context

            with create_progress_context(
                    "Получение шаблона деплоя...",
            ) as progress_callback:
                # Получаем шаблон
                template = api.get_template(
                    repo_name, stack_id, version, git_ref, progress=progress_callback
                )

            # Выводим основную информацию в стиле других команд get (только если не --no-headers)
            if not no_headers:
                console.print(
                    f"[bold white]NAME:[/bold white] {stack_id}[dim]@{namespace}[/dim]"
                )
                console.print(f"[bold white]NAMESPACE:[/bold white] {namespace}")
                console.print(f"[bold white]VERSION:[/bold white] {version}")
                console.print(f"[bold white]REPO:[/bold white] {repo_name}")
                console.print(f"[bold white]COMMIT:[/bold white] {git_ref}")
                console.print()

            # Выводим шаблон
            console.print(template)

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка получения шаблона: {e}[/red]")
        raise click.Abort()
