"""
Команды для управления нодами
"""

import click
from rich.console import Console

from core.api_client import ImagenariumAPIError
from core.services.nodes_service import NodesService
from utils.formatters import format_table, format_output, show_console_header

console = Console()


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
    """Управление нодами кластера"""
    pass


@cli.command("list")
@click.option(
    "--columns",
    help='Столбцы для отображения. Форматы: "NAME,STATUS" или "+TOTAL_MEMORY,-ID". Доступные: NAME, IP, ROLE, AVAILABILITY, STATUS, DC, DOCKER_VERSION, TOTAL_MEMORY, SSH_PORT, SSH_USER, EXTERNAL_URL, ID',
)
@click.option(
    "--filter",
    multiple=True,
    help="Фильтрация данных. Формат: COLUMN=value, COLUMN!=value, COLUMN~pattern. Примеры: STATUS=READY, ROLE=manager, IP~10.9",
)
@click.option("--no-cache", is_flag=True, help="Отключить кэширование")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option(
    "--output",
    "-o",
    help='Формат вывода данных: json, yaml, tsv, или template (например: "{NAME} - {STATUS}")',
)
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def list_nodes(ctx, columns, filter, no_cache, no_headers, output, verbose):
    """Показывает список нод

    По умолчанию: NAME, IP, ROLE, AVAILABILITY, STATUS. Дополнительные: DC, DOCKER_VERSION, TOTAL_MEMORY, SSH_PORT, SSH_USER, EXTERNAL_URL, ID
    """
    try:
        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли (скрываем при --no-headers или --output)
        show_console_header(api, show_header=not (no_headers or output))

        # Используем сервис нод (кеш-ориентированный)
        svc = NodesService(api_client=api)

        # Используем callback для прогресс-бара (вызывается только при реальных запросах)
        from core.progress import create_progress_context

        with create_progress_context(
                "Получение списка нод...",
        ) as progress_callback:
            # columns_spec передается в list, где он парсится и применяется
            data = svc.list(
                filters=list(filter) if filter else None,
                columns_spec=columns,
                no_cache=no_cache,
                progress=progress_callback,
            )
        if not data:
            console.print("Ноды не найдены")
            return

        # Определяем колонки для отображения (данные уже отфильтрованы в list)
        from utils.formatters import parse_filters

        # Если columns указан, используем столбцы из данных, иначе default
        if columns and data:
            columns_to_show = list(data[0].keys()) if data else svc.get_default_columns()
        else:
            columns_to_show = svc.get_default_columns()

        # Отображаем данные в указанном формате
        if not output or output == "table":
            # Передаем фильтры для подсветки совпадений
            highlight_filters = parse_filters(list(filter)) if filter else None
            format_table(
                data,
                columns=columns_to_show,
                no_headers=no_headers,
                highlight_filters=highlight_filters,
            )
        else:
            format_output(data, output, columns=columns_to_show)

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка получения списка нод: {e}[/red]")
        raise click.Abort()


@cli.command("get")
@click.argument("node_name")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def get_node(ctx, node_name, verbose):
    """Показывает информацию о конкретной ноде"""
    try:
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли
        show_console_header(api)

        # Используем сервис для получения данных в унифицированном формате
        svc = NodesService(api_client=api)

        # Используем callback для прогресс-бара (вызывается только при реальных запросах)
        from core.progress import create_progress_context

        with create_progress_context(
                "Загрузка информации о ноде...",
        ) as progress_callback:
            node = svc.get(node_name, progress=progress_callback)

        if not node:
            console.print(f"[red]Нода с именем {node_name} не найдена[/red]")
            return

        # Выводим детальную информацию о ноде (данные в snake_case)

        # Основные параметры
        from utils.formatters import print_field

        print_field(node, "name", default="N/A", skip_empty=False)
        print_field(node, "ip", default="N/A", skip_empty=False)
        print_field(node, "role", default="N/A", skip_empty=False)
        print_field(node, "dc")

        # Статус с цветовым кодированием
        from utils.highlighter import Highlighter

        status = node.get("status", "N/A")
        styled_status = Highlighter.highlight(status, check_partial=True)
        console.print(f"[bold white]STATUS:[/bold white] {styled_status}")

        # Доступность с цветовым кодированием
        availability = node.get("availability", "N/A")
        styled_availability = Highlighter.highlight(availability, check_partial=False)
        console.print(f"[bold white]AVAILABILITY:[/bold white] {styled_availability}")

        # Системная информация
        print_field(node, "docker_version")
        print_field(node, "total_memory")
        print_field(node, "ssh_port")
        print_field(node, "ssh_user")
        print_field(node, "external_url")
        print_field(node, "id")

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка получения информации о ноде: {e}[/red]")
        raise click.Abort()


@cli.command("update")
@click.argument("node_name")
@click.option("--hostname", help="Новое имя хоста")
@click.option("--role", help="Новая роль")
@click.option("--availability", help="Новая доступность")
@click.option("--external-url", help="Новый внешний URL")
@click.option("--ssh-port", help="Новый SSH порт")
@click.option("--ssh-user", help="Новый SSH пользователь")
@click.option(
    "--label", multiple=True, help="Добавить/обновить label (формат: key=value)"
)
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def update_node(
        ctx,
        node_name,
        hostname,
        role,
        availability,
        external_url,
        ssh_port,
        ssh_user,
        label,
        verbose,
):
    """Обновляет информацию о ноде"""
    try:
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Используем сервис для получения данных
        from core.progress import create_progress_context

        with create_progress_context(
                "Загрузка информации о ноде...",
        ) as progress_callback:
            # Используем сервис вместо прямого API вызова
            svc = NodesService(api_client=api)
            nodes_list = svc.list(progress=progress_callback)

            # Конвертируем в старый формат для совместимости
            nodes = []
            for node_data in nodes_list:
                nodes.append({
                    "hostname": node_data.get("name", ""),
                    "id": node_data.get("id", ""),
                    "ip": node_data.get("ip", ""),
                    "role": node_data.get("role", ""),
                    "availability": node_data.get("availability", ""),
                    "status": node_data.get("status", ""),
                    "dc": node_data.get("dc", ""),
                    "dockerVersion": node_data.get("docker_version", ""),
                    "totalMemory": node_data.get("total_memory", ""),
                    "sshPort": node_data.get("ssh_port", ""),
                    "sshUser": node_data.get("ssh_user", ""),
                    "externalUrl": node_data.get("external_url", ""),
                })

        # Находим ноду по имени
        node = next((n for n in nodes if n.get("hostname") == node_name), None)
        if not node:
            console.print(f"[red]Нода с именем {node_name} не найдена[/red]")
            return

        node_id = node.get("id")

        # Собираем данные для обновления (используем snake_case)
        update_data = {}

        if hostname:
            update_data["hostname"] = hostname
        if role:
            update_data["role"] = role
        if availability:
            update_data["availability"] = availability
        if external_url:
            update_data["external_url"] = external_url
        if ssh_port:
            update_data["ssh_port"] = ssh_port
        if ssh_user:
            update_data["ssh_user"] = ssh_user

        # Обрабатываем labels
        if label:
            labels = {}
            for l in label:
                if "=" in l:
                    key, value = l.split("=", 1)
                    labels[key] = value
                else:
                    console.print(
                        f"[yellow]Пропускаем неправильный label: {l}[/yellow]"
                    )
            if labels:
                update_data["labels"] = labels

        if not update_data:
            console.print("[yellow]Нет данных для обновления[/yellow]")
            return

        # Используем сервис для обновления
        svc = NodesService(api_client=api)
        svc.update(node_id, update_data)
        console.print(f"[green]Нода {node_name} успешно обновлена[/green]")

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка обновления ноды: {e}[/red]")
        raise click.Abort()
