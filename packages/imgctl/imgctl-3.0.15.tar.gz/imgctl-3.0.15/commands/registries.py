"""
Команды для управления реестрами
"""

import click
from rich.console import Console

from core.api_client import ImagenariumAPIError
from core.services.registries_service import RegistriesService
from utils.formatters import format_table, show_console_header

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
    """Управление реестрами образов"""
    pass


@cli.command("list")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option("--no-cache", is_flag=True, help="Отключить кэширование")
@click.option(
    "--output",
    "-o",
    help='Формат вывода данных: json, yaml, tsv, или template (например: "{NAME} - {URL}")',
)
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def list_registries(ctx, no_headers, no_cache, output, verbose):
    """Показывает список реестров"""
    try:
        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=False, ctx=ctx)

        # Показываем заголовок консоли (скрываем при --no-headers или --output)
        show_console_header(api, show_header=not (no_headers or output))

        svc = RegistriesService(api_client=api)

        # Используем callback для прогресс-бара (вызывается только при реальных запросах)
        from core.progress import create_progress_context

        with create_progress_context(
                "Получение списка реестров...",
        ) as progress_callback:
            data = svc.list(filters=None, columns_spec=None, no_cache=no_cache, progress=progress_callback)
        if not data:
            console.print("Реестры не найдены")
            return

        # Выводим данные в указанном формате
        if not output or output == "table":
            format_table(data, no_headers=no_headers)
        else:
            from utils.formatters import format_output

            format_output(data, output)

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка получения списка реестров: {e}[/red]")
        raise click.Abort()


@cli.command("add")
@click.option("--name", required=True, help="Имя реестра")
@click.option("--url", required=True, help="URL реестра")
@click.option("--username", required=True, help="Имя пользователя")
@click.option("--password", required=True, help="Пароль")
@click.pass_context
def add_registry(ctx, name, url, username, password):
    """Добавляет новый реестр"""
    try:
        api = _get_api_client(verbose=False, ctx=ctx)

        registry_info = {
            "name": name,
            "url": url,
            "username": username,
            "password": password,
        }

        console.print(f"[blue]Добавление реестра {name}...[/blue]")
        svc = RegistriesService(api_client=api)
        svc.add(registry_info)
        console.print(f"[green]Реестр {name} успешно добавлен[/green]")

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка добавления реестра: {e}[/red]")
        raise click.Abort()


@cli.command("delete")
@click.argument("registry_id")
@click.pass_context
def delete_registry(ctx, registry_id):
    """Удаляет реестр"""
    try:
        api = _get_api_client(verbose=False, ctx=ctx)

        console.print(f"[blue]Удаление реестра {registry_id}...[/blue]")
        svc = RegistriesService(api_client=api)
        svc.delete(registry_id)
        console.print(f"[green]Реестр {registry_id} успешно удален[/green]")

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка удаления реестра: {e}[/red]")
        raise click.Abort()
