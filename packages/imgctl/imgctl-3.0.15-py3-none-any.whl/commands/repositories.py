"""
Команды для управления репозиториями
"""

import click
from rich.console import Console

from core.api_client import ImagenariumAPIError
from core.services.repositories_service import RepositoriesService
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
    """Управление репозиториями"""
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
def list_repositories(ctx, no_headers, no_cache, output, verbose):
    """Показывает список репозиториев"""
    try:
        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли (скрываем при --no-headers или --output)
        show_console_header(api, show_header=not (no_headers or output))

        svc = RepositoriesService(api_client=api)

        # Используем callback для прогресс-бара (вызывается только при реальных запросах)
        from core.progress import create_progress_context

        with create_progress_context(
                "Получение списка репозиториев...",
        ) as progress_callback:
            data = svc.list(filters=None, columns_spec=None, no_cache=no_cache, progress=progress_callback)
        if not data:
            console.print("Репозитории не найдены")
            return

        # Выводим данные в указанном формате
        if not output or output == "table":
            format_table(data, no_headers=no_headers)
        else:
            from utils.formatters import format_output

            format_output(data, output)

        # Показываем дополнительную информацию о коммитах
        # Примечание: lastCommitInfo может быть в сырых данных API, а не в унифицированном формате
        # Для отображения коммитов нужно использовать api.get_repositories напрямую
        # Пока оставляем закомментированным, т.к. данные из сервиса в snake_case формате

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка получения списка репозиториев: {e}[/red]")
        raise click.Abort()


@cli.command("add")
@click.option("--name", required=True, help="Имя репозитория")
@click.option("--url", required=True, help="URL репозитория")
@click.option("--username", help="Имя пользователя")
@click.option("--password", help="Пароль")
@click.option("--offline", is_flag=True, help="Офлайн репозиторий")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def add_repository(ctx, name, url, username, password, offline, verbose):
    """Добавляет новый репозиторий"""
    try:
        api = _get_api_client(verbose=verbose, ctx=ctx)

        repository_info = {"name": name, "url": url, "offline": offline}

        if username:
            repository_info["username"] = username
        if password:
            repository_info["password"] = password

        console.print(f"[blue]Добавление репозитория {name}...[/blue]")
        svc = RepositoriesService(api_client=api)
        svc.add(repository_info)
        console.print(f"[green]Репозиторий {name} успешно добавлен[/green]")

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка добавления репозитория: {e}[/red]")
        raise click.Abort()


@cli.command("delete")
@click.argument("repository_id")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def delete_repository(ctx, repository_id, verbose):
    """Удаляет репозиторий"""
    try:
        api = _get_api_client(verbose=verbose, ctx=ctx)

        console.print(f"[blue]Удаление репозитория {repository_id}...[/blue]")
        svc = RepositoriesService(api_client=api)
        svc.delete(repository_id)
        console.print(f"[green]Репозиторий {repository_id} успешно удален[/green]")

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка удаления репозитория: {e}[/red]")
        raise click.Abort()
