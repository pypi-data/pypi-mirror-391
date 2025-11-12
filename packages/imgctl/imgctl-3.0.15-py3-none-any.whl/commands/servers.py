"""
Команды для управления серверами
"""

import os

import click
from rich.console import Console
from rich.table import Table

from core.api_client import ImagenariumAPIError
from core.cache_manager import CacheManager
from core.services.servers_service import ServersService
from utils.formatters import format_table, format_output, show_console_header

console = Console()


def _get_cache_manager() -> CacheManager:
    """Создает CacheManager для управления настройками TTL"""
    return CacheManager()


@click.group()
def cli():
    """Управление серверами и подключениями к «Imagenarium»"""
    pass


@cli.command("list")
@click.option(
    "--show-passwords", is_flag=True, help="Показывать пароли (не рекомендуется)"
)
@click.option(
    "--columns",
    help='Столбцы для отображения. Форматы: "NAME,URL" или "+DESCRIPTION,-DEFAULT". Доступные: NAME, URL, USERNAME, DESCRIPTION, DEFAULT, PASSWORD',
)
@click.option(
    "--filter",
    multiple=True,
    help="Фильтрация данных. Формат: COLUMN=value, COLUMN!=value, COLUMN~pattern. Примеры: NAME=dev, URL~harbor, DEFAULT=✓",
)
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option(
    "--output",
    "-o",
    help='Формат вывода данных: json, yaml, tsv, или template (например: "{NAME} - {URL}")',
)
@click.pass_context
def list_servers(ctx, show_passwords, columns, filter, no_headers, output):
    """Показывает список серверов"""
    try:
        svc = ServersService()

        # Получаем данные из сервиса (в snake_case)
        # columns_spec передается в list, где он парсится и применяется
        data = svc.list(
            filters=list(filter) if filter else None,
            columns_spec=columns,
        )

        if not data:
            console.print(
                "[yellow]Серверы не найдены. Добавьте сервер командой 'servers add'[/yellow]"
            )
            return

        # Опционально подгружаем пароль из сервиса, если запрошено
        if show_passwords:
            svc = ServersService()
            for row in data:
                server_name = row.get("name", "")
                if server_name:
                    password = svc._get_password(server_name)
                    row["password"] = password or ""

        # Определяем столбцы для вывода (данные уже отфильтрованы в list)
        from utils.formatters import parse_filters

        # Если columns указан, используем столбцы из данных, иначе default
        if columns and data:
            columns_to_show = list(data[0].keys())
            # Добавляем password если show_passwords и его еще нет
            if show_passwords and "password" not in columns_to_show:
                columns_to_show.append("password")
        else:
            columns_to_show = svc.get_default_columns()
            if show_passwords and "password" not in columns_to_show:
                columns_to_show.append("password")

        # Данные уже отфильтрованы по столбцам в list, но нужно убедиться что password есть если нужно
        filtered_data = []
        for row in data:
            filtered_row = {col: row.get(col, "") for col in columns_to_show}
            if filtered_row:
                filtered_data.append(filtered_row)

        # Отображаем данные в указанном формате
        if not output or output == "table":
            highlight_filters = parse_filters(list(filter)) if filter else None
            format_table(
                filtered_data,
                columns=columns_to_show,
                no_headers=no_headers,
                highlight_filters=highlight_filters,
            )
        else:
            format_output(filtered_data, output, columns=columns_to_show)

    except Exception as e:
        console.print(f"[red]Ошибка получения списка серверов: {e}[/red]")
        raise click.Abort()


@cli.command("add")
@click.argument("name")
@click.option("--url", required=True, help="URL сервера")
@click.option("--username", required=True, help="Имя пользователя")
@click.option("--password", required=True, help="Пароль")
@click.option("--description", help="Описание сервера")
@click.option(
    "--default", "is_default", is_flag=True, help="Установить как сервер по умолчанию"
)
@click.option(
    "--ttl",
    multiple=True,
    help="Настройки TTL в формате endpoint:ttl (например: /deployments/list:15)",
)
@click.pass_context
def add_server(ctx, name, url, username, password, description, is_default, ttl):
    """Добавляет новый сервер"""
    try:
        svc = ServersService()
        svc.add_server(name, url, username, password, description, is_default)

        console.print(f"[green]Сервер '{name}' успешно добавлен[/green]")

        if is_default:
            console.print(
                f"[blue]Сервер '{name}' установлен как сервер по умолчанию[/blue]"
            )

        # Обрабатываем настройки TTL
        if ttl:
            cache_manager = _get_cache_manager()
            base_rules = cache_manager._get_default_rules()

            console.print(f"\n[bold]Настройка TTL для сервера '{name}':[/bold]")

            for ttl_setting in ttl:
                try:
                    if ":" not in ttl_setting:
                        console.print(
                            f"[red]Ошибка: Неверный формат TTL '{ttl_setting}'. Используйте endpoint:ttl[/red]"
                        )
                        continue

                    endpoint, ttl_value = ttl_setting.split(":", 1)
                    ttl_value = int(ttl_value)

                    # Проверяем, существует ли эндпоинт
                    if endpoint not in base_rules:
                        console.print(
                            f"[red]Ошибка: Эндпоинт '{endpoint}' не найден[/red]"
                        )
                        console.print(
                            f"[yellow]Доступные эндпоинты: {', '.join(base_rules.keys())}[/yellow]"
                        )
                        continue

                    # Устанавливаем TTL
                    cache_manager.set_server_ttl(name, endpoint, ttl_value)
                    console.print(f"[green]  {endpoint}: {ttl_value} сек[/green]")

                except ValueError:
                    console.print(
                        f"[red]Ошибка: Неверное значение TTL '{ttl_value}'. Должно быть числом[/red]"
                    )
                except Exception as e:
                    console.print(
                        f"[red]Ошибка установки TTL для '{endpoint}': {e}[/red]"
                    )

    except ValueError as e:
        console.print(f"[red]Ошибка: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Ошибка добавления сервера: {e}[/red]")
        raise click.Abort()


@cli.command("remove")
@click.argument("name")
@click.option("--confirm", is_flag=True, help="Подтвердить удаление без запроса")
@click.pass_context
def remove_server(ctx, name, confirm):
    """Удаляет сервер"""
    try:
        svc = ServersService()

        if not confirm:
            if not click.confirm(f"Вы уверены, что хотите удалить сервер '{name}'?"):
                console.print("[yellow]Удаление отменено[/yellow]")
                return

        svc.remove_server(name)
        console.print(f"[green]Сервер '{name}' успешно удален[/green]")

    except ValueError as e:
        console.print(f"[red]Ошибка: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Ошибка удаления сервера: {e}[/red]")
        raise click.Abort()


@cli.command("set-default")
@click.argument("name")
@click.pass_context
def set_default_server(ctx, name):
    """Устанавливает сервер по умолчанию"""
    try:
        svc = ServersService()
        svc.set_default_server(name)
        console.print(
            f"[green]Сервер '{name}' установлен как сервер по умолчанию[/green]"
        )

    except ValueError as e:
        console.print(f"[red]Ошибка: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Ошибка установки сервера по умолчанию: {e}[/red]")
        raise click.Abort()


@cli.command("test")
@click.argument("name")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.pass_context
def test_server(ctx, name, no_headers):
    """Тестирует подключение к серверу"""
    try:
        svc = ServersService()
        config = svc.get_config_for_server(name)

        from core.api_client import ImagenariumAPIClient

        api = ImagenariumAPIClient(config, server_name=name)

        # Показываем заголовок консоли
        show_console_header(api, show_header=not no_headers)

        console.print(f"[blue]Тестирование подключения к серверу '{name}'...[/blue]")
        version = api.get_version()
        console.print(
            f"[green]✓ Подключение успешно! Версия «Imagenarium»: {version}[/green]"
        )

    except ValueError as e:
        console.print(f"[red]Ошибка: {e}[/red]")
        raise click.Abort()
    except ImagenariumAPIError as e:
        console.print(f"[red]✗ Ошибка подключения: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]✗ Неожиданная ошибка: {e}[/red]")
        raise click.Abort()


@cli.command("update")
@click.argument("name")
@click.option("--url", help="Новый URL сервера")
@click.option("--username", help="Новое имя пользователя")
@click.option("--password", help="Новый пароль")
@click.option("--description", help="Новое описание")
@click.option(
    "--default", "is_default", is_flag=True, help="Установить как сервер по умолчанию"
)
@click.option(
    "--ttl",
    multiple=True,
    help="Настройки TTL в формате endpoint:ttl (например: /deployments/list:15)",
)
@click.pass_context
def update_server(ctx, name, url, username, password, description, is_default, ttl):
    """Обновляет информацию о сервере"""
    try:
        svc = ServersService()

        # Собираем параметры для обновления
        update_params = {}
        if url:
            update_params["url"] = url
        if username:
            update_params["username"] = username
        if password:
            update_params["password"] = password
        if description is not None:
            update_params["description"] = description
        if is_default:
            update_params["is_default"] = True

        if not update_params:
            console.print("[yellow]Нет параметров для обновления[/yellow]")
            return

        svc.update_server(name, **update_params)
        console.print(f"[green]Сервер '{name}' успешно обновлен[/green]")

        # Обрабатываем настройки TTL
        if ttl:
            cache_manager = _get_cache_manager()
            base_rules = cache_manager._get_default_rules()

            console.print(f"\n[bold]Обновление TTL для сервера '{name}':[/bold]")

            for ttl_setting in ttl:
                try:
                    if ":" not in ttl_setting:
                        console.print(
                            f"[red]Ошибка: Неверный формат TTL '{ttl_setting}'. Используйте endpoint:ttl[/red]"
                        )
                        continue

                    endpoint, ttl_value = ttl_setting.split(":", 1)
                    ttl_value = int(ttl_value)

                    # Проверяем, существует ли эндпоинт
                    if endpoint not in base_rules:
                        console.print(
                            f"[red]Ошибка: Эндпоинт '{endpoint}' не найден[/red]"
                        )
                        console.print(
                            f"[yellow]Доступные эндпоинты: {', '.join(base_rules.keys())}[/yellow]"
                        )
                        continue

                    # Устанавливаем TTL
                    cache_manager.set_server_ttl(name, endpoint, ttl_value)
                    console.print(f"[green]  {endpoint}: {ttl_value} сек[/green]")

                except ValueError:
                    console.print(
                        f"[red]Ошибка: Неверное значение TTL '{ttl_value}'. Должно быть числом[/red]"
                    )
                except Exception as e:
                    console.print(
                        f"[red]Ошибка установки TTL для '{endpoint}': {e}[/red]"
                    )

    except ValueError as e:
        console.print(f"[red]Ошибка: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Ошибка обновления сервера: {e}[/red]")
        raise click.Abort()


@cli.command("get")
@click.argument("name")
@click.option("--no-cache", is_flag=True, help="Отключить кэширование")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Формат вывода",
)
@click.pass_context
def get_server(ctx, name, no_cache, verbose, no_headers, output_format):
    """Показывает детальную информацию о сервере и настройки TTL"""
    try:
        # ServersService читает из конфига, не нужен прогресс-бар
        svc = ServersService()
        server = svc.get_server(name)

        if not server:
            console.print(f"[red]Сервер '{name}' не найден[/red]")
            return

        # Показываем заголовок консоли (только для table формата и если не отключен)
        if output_format == "table" and not no_headers:
            header_shown = False
            try:
                from core.api_client import ImagenariumAPIClient

                config = svc.get_config_for_server(name)
                api = ImagenariumAPIClient(config, server_name=name)
                # Пытаемся получить конфиг консоли
                config_data = api.get_console_config()
                console_name = config_data.get("consoleName", server.name)
                console_color = config_data.get("consoleColor", "#666666")

                # Пытаемся получить версию
                try:
                    version = api.get_version(no_cache=True)
                except Exception:
                    version = None

                from utils.formatters import display_console_header

                display_console_header(console_name, console_color, version)
                header_shown = True
            except Exception:
                pass

            # Fallback заголовок если сервер недоступен
            if not header_shown:
                from utils.formatters import display_console_header

                display_console_header(
                    f"Imagenarium: {server.name} (недоступен)", "#666666"
                )

        # Получаем настройки TTL для сервера
        cache_manager = _get_cache_manager()
        server_ttl_settings = cache_manager.get_server_ttl_settings(name)

        if output_format == "table":
            # Выводим основную информацию в стиле других команд get
            console.print(f"[bold white]NAME:[/bold white] {server.name}")
            console.print(f"[bold white]URL:[/bold white] {server.url}")
            console.print(
                f"[bold white]USERNAME:[/bold white] {server.username or 'не указан'}"
            )
            console.print(
                f"[bold white]DESCRIPTION:[/bold white] {server.description or 'не указано'}"
            )
            console.print(
                f"[bold white]DEFAULT:[/bold white] {'✓' if server.is_default else '✗'}"
            )

            # Получаем и выводим версию Imagenarium
            try:
                from core.api_client import ImagenariumAPIClient

                config = svc.get_config_for_server(name)
                api = ImagenariumAPIClient(config, server_name=name)
                version = api.get_version(no_cache=True)
                console.print(f"[bold white]VERSION:[/bold white] {version}")
            except Exception:
                console.print(
                    f"[bold white]VERSION:[/bold white] [red]недоступна[/red]"
                )

            # Настройки TTL
            console.print(f"\n[bold white]TTL:[/bold white]")

            # Получаем пользовательские настройки TTL
            ttl_overrides = {}
            if server_ttl_settings and "ttl_overrides" in server_ttl_settings:
                ttl_overrides = server_ttl_settings["ttl_overrides"]

            # Получаем глобальные настройки
            base_rules = cache_manager._get_default_rules()

            # Показываем все эндпоинты с текущими и дефолтными значениями
            for endpoint, rule in base_rules.items():
                # Определяем текущее значение TTL
                current_ttl = ttl_overrides.get(endpoint, rule["ttl"])
                default_ttl = rule["ttl"]

                # Форматируем текущее значение
                if current_ttl == 0:
                    current_display = f"[red]{current_ttl} сек[/red]"
                elif current_ttl < 60:
                    current_display = f"[yellow]{current_ttl} сек[/yellow]"
                else:
                    current_display = f"[green]{current_ttl} сек[/green]"

                # Форматируем дефолтное значение
                if default_ttl == 0:
                    default_display = f"[red]{default_ttl} сек[/red]"
                elif default_ttl < 60:
                    default_display = f"[yellow]{default_ttl} сек[/yellow]"
                else:
                    default_display = f"[green]{default_ttl} сек[/green]"

                # Показываем значение с указанием дефолтного
                if current_ttl == default_ttl:
                    console.print(f"  {endpoint:<25}: {current_display}")
                else:
                    console.print(
                        f"  {endpoint:<25}: {current_display} (default: {default_display})"
                    )

        elif output_format == "json":
            import json

            # Получаем версию для JSON формата
            version = None
            try:
                from core.api_client import ImagenariumAPIClient

                config = svc.get_config_for_server(name)
                api = ImagenariumAPIClient(config, server_name=name)
                version = api.get_version(no_cache=True)
            except Exception:
                pass

            result = {
                "server": {
                    "name": server.name,
                    "url": server.url,
                    "username": server.username,
                    "description": server.description,
                    "is_default": server.is_default,
                    "version": version,
                },
                "ttl_settings": server_ttl_settings,
                "global_ttl_settings": cache_manager._get_default_rules(),
            }
            console.print(json.dumps(result, indent=2, ensure_ascii=False))

        elif output_format == "yaml":
            import yaml

            # Получаем версию для YAML формата
            version = None
            try:
                from core.api_client import ImagenariumAPIClient

                config = svc.get_config_for_server(name)
                api = ImagenariumAPIClient(config, server_name=name)
                version = api.get_version(no_cache=True)
            except Exception:
                pass

            result = {
                "server": {
                    "name": server.name,
                    "url": server.url,
                    "username": server.username,
                    "description": server.description,
                    "is_default": server.is_default,
                    "version": version,
                },
                "ttl_settings": server_ttl_settings,
                "global_ttl_settings": cache_manager._get_default_rules(),
            }
            console.print(
                yaml.dump(result, default_flow_style=False, allow_unicode=True)
            )

    except Exception as e:
        console.print(f"[red]Ошибка при получении информации о сервере: {e}[/red]")
        raise click.Abort()


@cli.group("cache")
def cache_group():
    """Управление настройками кеширования"""
    pass


@cache_group.command("show")
@click.option("--server", "-s", help="Показать настройки для конкретного сервера")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Формат вывода",
)
@click.pass_context
def show_cache_settings(ctx, server, output_format):
    """Показывает текущие настройки TTL для всех эндпоинтов"""
    try:
        # Создаем CacheManager для получения правил кеширования
        cache_manager = CacheManager()

        # Если сервер не указан, пытаемся получить из контекста
        if not server:
            # Проверяем, есть ли глобальные опции сервера
            if hasattr(ctx, "obj") and ctx.obj and "server" in ctx.obj:
                server = ctx.obj["server"]
            # Или из переменной окружения
            elif "IMG_SERVER" in os.environ:
                server = os.environ["IMG_SERVER"]

        if server:
            # Показываем настройки для конкретного сервера
            server_settings = cache_manager.get_server_ttl_settings(server)
            if not server_settings:
                console.print(
                    f"[yellow]Настройки для сервера '{server}' не найдены[/yellow]"
                )
                console.print(
                    "[yellow]Используются глобальные настройки по умолчанию[/yellow]"
                )
                server_settings = {}

            # Получаем базовые правила
            base_rules = cache_manager._get_default_rules()

            # Создаем объединенные правила
            rules = {}
            for endpoint, rule in base_rules.items():
                rules[endpoint] = rule.copy()
                # Применяем сервер-специфичные настройки
                if "ttl_overrides" in server_settings:
                    if endpoint in server_settings["ttl_overrides"]:
                        rules[endpoint]["ttl"] = server_settings["ttl_overrides"][
                            endpoint
                        ]
        else:
            # Показываем глобальные настройки
            rules = cache_manager._cache_rules

        if output_format == "table":
            # Создаем таблицу
            table = Table(title="Настройки кеширования TTL")
            table.add_column("Эндпоинт", style="cyan", no_wrap=True)
            table.add_column("TTL (сек)", style="green", justify="right")
            table.add_column("Описание", style="white")
            table.add_column("Стратегия", style="blue")

            # Добавляем правила в таблицу
            for endpoint, rule in rules.items():
                ttl_display = f"{rule['ttl']} сек"
                if rule["ttl"] == 0:
                    ttl_display = "[red]0 сек (всегда обновляется)[/red]"
                elif rule["ttl"] < 60:
                    ttl_display = (
                        f"[yellow]{rule['ttl']} сек (быстрое обновление)[/yellow]"
                    )
                else:
                    ttl_display = f"[green]{rule['ttl']} сек[/green]"

                table.add_row(
                    endpoint, ttl_display, rule["description"], rule["strategy"]
                )

            console.print(table)

            # Показываем информацию о сервере, если указан
            if server:
                console.print(f"\n[bold]Настройки для сервера: {server}[/bold]")
                console.print(
                    "[yellow]Примечание: TTL настройки глобальные для всех серверов[/yellow]"
                )
            else:
                console.print(f"\n[bold]Всего правил кеширования: {len(rules)}[/bold]")
                console.print(
                    "[yellow]Примечание: TTL настройки глобальные для всех серверов[/yellow]"
                )

        elif output_format == "json":
            import json

            result = {
                "cache_settings": rules,
                "note": "TTL настройки глобальные для всех серверов",
            }
            if server:
                result["server"] = server
            console.print(json.dumps(result, indent=2, ensure_ascii=False))

        elif output_format == "yaml":
            import yaml

            result = {
                "cache_settings": rules,
                "note": "TTL настройки глобальные для всех серверов",
            }
            if server:
                result["server"] = server
            console.print(
                yaml.dump(result, default_flow_style=False, allow_unicode=True)
            )

    except Exception as e:
        console.print(f"[red]Ошибка при получении настроек кеширования: {e}[/red]")
        raise click.Abort()


@cache_group.command("set")
@click.argument("endpoint")
@click.argument("ttl", type=int)
@click.option("--server", "-s", help="Установить настройку для конкретного сервера")
@click.pass_context
def set_cache_ttl(ctx, endpoint, ttl, server):
    """Устанавливает TTL для конкретного эндпоинта"""
    try:
        if ttl < 0:
            console.print("[red]Ошибка: TTL не может быть отрицательным[/red]")
            raise click.Abort()

        # Если сервер не указан, пытаемся получить из контекста
        if not server:
            # Проверяем, есть ли глобальные опции сервера
            if hasattr(ctx, "obj") and ctx.obj and "server" in ctx.obj:
                server = ctx.obj["server"]
            # Или из переменной окружения
            elif "IMG_SERVER" in os.environ:
                server = os.environ["IMG_SERVER"]

        # Создаем CacheManager
        cache_manager = CacheManager()

        # Проверяем, существует ли эндпоинт
        base_rules = cache_manager._get_default_rules()
        if endpoint not in base_rules:
            console.print(f"[red]Ошибка: Эндпоинт '{endpoint}' не найден[/red]")
            console.print(
                f"[yellow]Доступные эндпоинты: {', '.join(base_rules.keys())}[/yellow]"
            )
            raise click.Abort()

        if server:
            # Устанавливаем TTL для конкретного сервера
            try:
                cache_manager.set_server_ttl(server, endpoint, ttl)
                console.print(
                    f"[green]TTL для '{endpoint}' на сервере '{server}' установлен в {ttl} сек[/green]"
                )
            except Exception as e:
                console.print(f"[red]Ошибка установки TTL для сервера: {e}[/red]")
                raise click.Abort()
        else:
            # Устанавливаем глобальный TTL
            old_ttl = cache_manager._cache_rules[endpoint]["ttl"]
            cache_manager._cache_rules[endpoint]["ttl"] = ttl
            cache_manager._save_user_config()
            console.print(
                f"[green]Глобальный TTL для '{endpoint}' изменен с {old_ttl} сек на {ttl} сек[/green]"
            )

        if ttl == 0:
            console.print(
                "[yellow]Эндпоинт будет всегда обновляться (кеширование отключено)[/yellow]"
            )
        elif ttl < 60:
            console.print(
                "[yellow]Эндпоинт будет обновляться быстро (частые запросы)[/yellow]"
            )
        else:
            console.print("[green]Эндпоинт будет кешироваться эффективно[/green]")

    except Exception as e:
        console.print(f"[red]Ошибка при установке TTL: {e}[/red]")
        raise click.Abort()


@cache_group.command("reset")
@click.option("--server", "-s", help="Сбросить настройки для конкретного сервера")
@click.confirmation_option(
    prompt="Вы уверены, что хотите сбросить настройки кеширования?"
)
@click.pass_context
def reset_cache_settings(ctx, server):
    """Сбрасывает настройки кеширования к значениям по умолчанию"""
    try:
        # Если сервер не указан, пытаемся получить из контекста
        if not server:
            # Проверяем, есть ли глобальные опции сервера
            if hasattr(ctx, "obj") and ctx.obj and "server" in ctx.obj:
                server = ctx.obj["server"]
            # Или из переменной окружения
            elif "IMG_SERVER" in os.environ:
                server = os.environ["IMG_SERVER"]

        if server:
            console.print(
                f"[yellow]Внимание: Сброс настроек для сервера '{server}' пока не поддерживается[/yellow]"
            )
            console.print(
                "[yellow]Настройки будут сброшены глобально для всех серверов[/yellow]"
            )

        # Создаем CacheManager
        cache_manager = CacheManager()

        # Сбрасываем кеш
        cache_manager.clear_cache()

        console.print(
            "[green]Настройки кеширования сброшены к значениям по умолчанию[/green]"
        )
        console.print("[yellow]Все кешированные данные очищены[/yellow]")

    except Exception as e:
        console.print(f"[red]Ошибка при сбросе настроек: {e}[/red]")
        raise click.Abort()
