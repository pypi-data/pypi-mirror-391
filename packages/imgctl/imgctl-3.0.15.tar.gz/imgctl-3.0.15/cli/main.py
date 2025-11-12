"""
Главный модуль CLI для imgctl
"""

import os

import click
from rich.console import Console

from commands import nodes, stacks, components, registries, repositories, servers, logs, shell
from core.api_client import ImagenariumAPIClient

console = Console()


def show_version():
    """Показать информацию о версии приложения"""
    VERSION = "3.0.15"
    print(
        f"imgctl v{VERSION} - Консольная утилита для управления контейнерной платформой «Imagenarium»"
    )
    print("Документация: https://gitlab.com/koden8/imgctl | Автор: @koden8")


def custom_help_callback(ctx, param, value):
    """Кастомный callback для help с локализацией"""
    if value and not ctx.resilient_parsing:
        show_extended_help()
        ctx.exit()


def show_extended_help():
    """Показывает расширенный help с командами и подкомандами в простом текстовом формате"""
    print(
        "imgctl v3.0.15 - Консольная утилита для управления контейнерной платформой «Imagenarium»"
    )
    print("Документация: https://gitlab.com/koden8/imgctl | Автор: @koden8")
    print()

    print("Глобальные параметры:")
    print("  --server, -s        Имя сервера или URL для подключения")
    print("  --username, -u      Имя пользователя (для прямого подключения)")
    print("  --password, -p      Пароль (для прямого подключения)")
    print("  --config, -c        Путь к файлу конфигурации")
    print("  --verbose, -v       Подробный вывод HTTP запросов")
    print("  --version           Показать версию")
    print("  --help, -h          Показать справку")
    print()

    print("Основные команды:")
    print("  components       Управление компонентами приложений")
    print("  stacks           Управление стеками приложений")
    print("  logs             Просмотр логов компонентов")
    print("  nodes            Управление нодами кластера")
    print("  registries       Управление реестрами образов")
    print("  repositories     Управление репозиториями")
    print("  servers          Управление серверами и подключениями")
    print("  shell            Интерактивная оболочка (REPL)")
    print()

    print("Команды components:")
    print("  list             Показывает список развернутых компонентов")
    print("  get              Показывает детальную информацию о компоненте")
    print("  start            Запускает компонент")
    print("  stop             Останавливает компонент")
    print("  tags             Показывает теги развертываний для компонента")
    print("  upgrade          Обновляет компоненты до указанных тегов")
    print()

    print("Команды stacks:")
    print("  list             Показывает список стеков")
    print("  get              Показывает детальную информацию о стеке")
    print("  deploy           Деплоит стек в namespace")
    print("  undeploy         Андеплоит стек из namespace")
    print(
        "  template         Получает шаблон деплоя (поддерживает 3 формата и режим --diff)"
    )
    print()

    print("Команды servers:")
    print("  list             Показывает список серверов")
    print("  add              Добавляет новый сервер")
    print("  remove           Удаляет сервер")
    print("  set-default      Устанавливает сервер по умолчанию")
    print()

    print("Справка:")
    print("  imgctl <команда> --help     Показать справку по команде")
    print("  imgctl --help               Показать общую справку")
    print("  imgctl --version            Показать версию")


def get_api_client(
        verbose: bool = False,
        server: str = None,
        username: str = None,
        password: str = None,
        config: str = None,
):
    """Создает и возвращает API клиент с заданными параметрами"""
    # Инициализация конфигурации
    cfg = None

    try:
        # Используем централизованный метод для определения конфигурации
        from core.services.servers_service import ServersService

        try:
            cfg = ServersService.get_config(
                server=server,
                username=username,
                password=password,
                config_path=config,
            )
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise click.Abort()

        # Определяем имя сервера для настроек TTL и кеша
        server_name_for_ttl = ServersService.get_current_server(server=server)

        # Если не удалось определить из параметров/окружения, пытаемся извлечь из конфигурации
        if not server_name_for_ttl and cfg and cfg.server:
            from core.services.servers_service import get_server_name_from_config_or_url
            server_name_for_ttl = get_server_name_from_config_or_url(server_url=cfg.server)

        # async_mode только в shell режиме
        is_shell_mode = os.getenv("IMGCTL_SHELL_MODE") == "1"

        # Инициализация API клиента с контекстом (подключение, async, кеширование)
        return ImagenariumAPIClient(
            config=cfg,
            verbose=verbose,
            async_mode=is_shell_mode,
            server_name=server_name_for_ttl
        )

    except Exception as e:
        console.print(f"[red]Ошибка инициализации: {e}[/red]")
        console.print(
            "[yellow]Попробуйте добавить сервер командой 'servers add'[/yellow]"
        )
        raise click.Abort()


@click.group(
    context_settings={"help_option_names": ["-h", "--help"], "show_default": False},
    invoke_without_command=True,
)
@click.option("--server", "-s", help="Имя сервера или URL для подключения")
@click.option("--username", "-u", help="Имя пользователя (для прямого подключения)")
@click.option("--password", "-p", help="Пароль (для прямого подключения)")
@click.option("--config", "-c", help="Путь к файлу конфигурации")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод")
@click.option(
    "--version",
    is_flag=True,
    help="Показать информацию о версии приложения",
    callback=lambda ctx, param, value: show_version() or ctx.exit() if value else None,
)
@click.option(
    "--help",
    "-h",
    is_flag=True,
    help="Показать это сообщение и выйти",
    callback=custom_help_callback,
)
@click.pass_context
def main(ctx, server, username, password, config, verbose, version, help):
    """imgctl - Консольная утилита для управления контейнерной платформой «Imagenarium»"""
    ctx.ensure_object(dict)

    ctx.obj["verbose"] = verbose
    ctx.obj["server"] = server
    ctx.obj["username"] = username
    ctx.obj["password"] = password
    ctx.obj["config"] = config

    # Если это главная команда без аргументов, показываем расширенный help
    if ctx.invoked_subcommand is None and not ctx.params.get("help"):
        show_extended_help()
        ctx.exit()

    # Если это команда servers или shell, не инициализируем API клиент
    if ctx.invoked_subcommand in ["servers", "shell"]:
        # Но для shell сохраняем все параметры для последующего использования
        # (они уже сохранены в ctx.obj выше)
        return

    # Если это команда с подкомандами без подкоманды, показываем help
    if ctx.invoked_subcommand in [
        "components",
        "stacks",
        "nodes",
        "registries",
        "repositories",
    ] and not ctx.params.get("help"):
        # Проверяем, есть ли подкоманда в args
        import sys

        if len(sys.argv) <= 2 or sys.argv[2] in ["-h", "--help"]:
            return

    # Если это команда с подкомандами, не создаем API клиент здесь
    if ctx.invoked_subcommand in [
        "components",
        "stacks",
        "nodes",
        "registries",
        "repositories",
    ]:
        return

    # Инициализация конфигурации
    cfg = None

    try:
        # Используем централизованный метод для определения конфигурации
        from core.services.servers_service import ServersService

        try:
            cfg = ServersService.get_config(
                server=server,
                username=username,
                password=password,
                config_path=config,
            )
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise click.Abort()

        ctx.obj["config"] = cfg

        # Определяем имя сервера для настроек TTL и кеша

        server_name_for_ttl = ServersService.get_current_server(server=server)

        # Если не удалось определить из параметров/окружения, пытаемся извлечь из конфигурации
        if not server_name_for_ttl and cfg and cfg.server:
            from core.services.servers_service import get_server_name_from_config_or_url
            server_name_for_ttl = get_server_name_from_config_or_url(server_url=cfg.server)

        # async_mode только в shell режиме
        is_shell_mode = os.getenv("IMGCTL_SHELL_MODE") == "1"

        # Инициализация API клиента с контекстом (подключение, async, кеширование)
        ctx.obj["api"] = ImagenariumAPIClient(
            config=cfg,
            verbose=verbose,
            async_mode=is_shell_mode,
            server_name=server_name_for_ttl
        )

    except Exception as e:
        console.print(f"[red]Ошибка инициализации: {e}[/red]")
        console.print(
            "[yellow]Попробуйте добавить сервер командой 'servers add'[/yellow]"
        )
        raise click.Abort()


# Добавляем команды
main.add_command(servers.cli, name="servers")
main.add_command(nodes.cli, name="nodes")
main.add_command(stacks.cli, name="stacks")
main.add_command(components.cli, name="components")
main.add_command(registries.cli, name="registries")
main.add_command(repositories.cli, name="repositories")
main.add_command(logs.logs, name="logs")
main.add_command(shell.shell, name="shell")

if __name__ == "__main__":
    main()
