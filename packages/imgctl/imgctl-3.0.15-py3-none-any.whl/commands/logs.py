#!/usr/bin/env python3
"""
Команды для работы с логами компонентов
"""

import html
import re
import time
import webbrowser

import click
from rich.console import Console
from rich.text import Text

from core.api_client import ImagenariumAPIError
from utils.formatters import show_console_header

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


def parse_log_line(line):
    """Парсит строку лога из SSE потока"""
    if not line.startswith("data:"):
        return None

    # Убираем префикс 'data:'
    html_content = line[5:]

    # Проверяем на служебные сообщения (ping, heartbeat и т.д.)
    if html_content.strip() in ["$ping$", "$heartbeat$", "ping", "pong", "keepalive"]:
        return {
            "timestamp": "",
            "level": "PING",
            "level_color": "",
            "message": html_content.strip(),
            "raw": line,
            "is_service": True,
        }

    # Извлекаем timestamp
    timestamp_match = re.search(
        r"<span style='color:#ffeca5'>(.*?)</span>", html_content
    )
    timestamp = timestamp_match.group(1) if timestamp_match else ""

    # Извлекаем уровень лога
    level_match = re.search(
        r"<span style='color:([^']+)'>\[(.*?)\]</span>", html_content
    )
    level = level_match.group(2) if level_match else ""
    level_color = level_match.group(1) if level_match else ""

    # Убираем все HTML теги и декодируем HTML-сущности
    clean_content = re.sub(r"<[^>]+>", "", html_content)
    clean_content = clean_content.replace("&nbsp;", " ")
    clean_content = html.unescape(clean_content)

    # Убираем timestamp и level из начала строки
    if timestamp:
        clean_content = clean_content.replace(timestamp, "", 1)
    if level:
        clean_content = clean_content.replace(f"[{level}]", "", 1)

    # Очищаем от лишних пробелов, но сохраняем переносы строк для многострочных сообщений
    clean_content = clean_content.strip()

    return {
        "timestamp": timestamp,
        "level": level,
        "level_color": level_color,
        "message": clean_content,
        "raw": line,
        "is_service": False,
    }


def format_log_line(log_data, show_timestamp=True):
    """Форматирует строку лога для вывода в консоль"""
    if not log_data:
        return ""

    # Пропускаем служебные сообщения (ping, heartbeat)
    if log_data.get("is_service", False):
        return None

    timestamp = log_data["timestamp"]
    level = log_data["level"]
    message = log_data["message"]
    is_service = log_data.get("is_service", False)

    # Создаем Rich Text объект для цветного вывода
    text = Text()

    if show_timestamp and timestamp:
        text.append(f"[{timestamp}] ", style="bright_yellow")

    # Цветовое кодирование уровня лога
    if level:
        if level.upper() == "ERROR":
            text.append(f"[{level}] ", style="bold red")
        elif level.upper() == "WARN":
            text.append(f"[{level}] ", style="bold yellow")
        elif level.upper() == "INFO":
            text.append(f"[{level}] ", style="bold blue")
        elif level.upper() == "DEBUG":
            text.append(f"[{level}] ", style="dim white")
        elif level.upper() == "PING":
            text.append(f"[{level}] ", style="dim cyan")
        else:
            text.append(f"[{level}] ", style="white")

    # Специальное форматирование для служебных сообщений
    if is_service:
        text.append(message, style="dim cyan")
    else:
        text.append(message, style="white")

    return text


def get_component_info(api, component_name, no_cache=False, verbose=True):
    """Получает информацию о компоненте, используя кэш"""
    if no_cache or not api.cache:
        return _find_component_in_list(api, component_name)

    # Используем новый метод поиска ID с кешированием на 1 час
    component_id = api.find_component_id_by_name(component_name)

    if not component_id:
        if verbose:
            console.print(f"[dim]Компонент {component_name} не найден[/dim]")
        return None

    # Если ID найден, получаем полную информацию о компоненте
    if verbose:
        console.print(
            f"[dim]Компонент {component_name} найден (ID: {component_id})[/dim]"
        )

    # Создаем минимальную информацию о компоненте с ID
    # Не вызываем _find_component_in_list, чтобы не сбрасывать кеш
    component_info = {"id": component_id, "name": component_name}

    return component_info


def _find_component_in_list(api, component_name):
    """Ищет компонент в списке развертываний"""
    try:
        components = api.get_components()

        for group in components:
            stacks = group.get("stacks", [])
            for stack in stacks:
                stack_components = stack.get("components", [])
                for comp in stack_components:
                    if comp.get("name") == component_name:
                        return comp
        return None
    except Exception as e:
        console.print(f"[dim]Ошибка поиска компонента: {e}[/dim]")
        return None


def stream_logs(api, component_id, lines=None, follow=False, level_filter=None):
    """Потоковое чтение логов компонента"""
    try:
        # Параметры запроса
        params = {"tzOffset": 0}

        # В режиме follow запрашиваем только последние записи
        if follow:
            params["follow"] = "true"
            # Если не указано количество строк, берем только последние 10
            if lines is None:
                params["lines"] = 10
                console.print(
                    "[dim]Режим follow: показываем последние 10 записей + новые[/dim]"
                )
            else:
                params["lines"] = lines
        elif lines:
            params["lines"] = lines

        # Заголовки для SSE
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Accept-Encoding": "gzip, deflate",
        }

        response = api.session.get(
            f"{api.base_url}/logs/{component_id}",
            params=params,
            headers=headers,
            stream=True,
            timeout=None if follow else 30,
        )

        if response.status_code == 404:
            # Пробрасываем ошибку 404 для обработки в вызывающем коде
            raise Exception(
                f"There is no container, service or task with ID = '{component_id}'"
            )
        elif response.status_code != 200:
            console.print(f"[red]Ошибка получения логов: {response.status_code}[/red]")
            return

        line_count = 0
        ping_count = 0
        processed_count = 0  # Счетчик всех обработанных строк
        start_time = time.time()

        # Буфер для накопления логов перед выводом (для правильного порядка)
        log_buffer = []
        # Переменная для отслеживания последнего timestamp и level
        last_timestamp = None
        last_level = None

        try:
            for line in response.iter_lines(decode_unicode=True):
                processed_count += 1
                if line and line.startswith("data:"):
                    # Парсим строку лога
                    log_data = parse_log_line(line)
                    if not log_data:
                        continue

                    # Считаем служебные сообщения отдельно
                    if log_data.get("is_service", False):
                        ping_count += 1
                        # Скрываем служебные сообщения
                        continue

                    # Фильтрация по уровню (только для обычных логов)
                    if (
                            level_filter
                            and not log_data.get("is_service", False)
                            and log_data["level"].upper() != level_filter.upper()
                    ):
                        continue

                    # Обработка многострочных сообщений
                    current_timestamp = log_data.get("timestamp", "")
                    current_level = log_data.get("level", "")
                    current_message = log_data.get("message", "")

                    # Если у текущей строки нет timestamp и level, но есть предыдущие,
                    # то это продолжение многострочного сообщения
                    if (
                            not current_timestamp
                            and not current_level
                            and last_timestamp
                            and last_level
                    ):
                        # Это продолжение предыдущего сообщения
                        # Проверяем, является ли это первой строкой ASCII art
                        if current_message and current_message.strip().startswith("."):
                            # Первая строка ASCII art - без timestamp, но с отступом
                            log_data["timestamp"] = ""
                            log_data["level"] = ""
                            # Добавляем отступ в начало сообщения для выравнивания
                            # Нужно добавить пробел в начало, чтобы выровнять с остальными строками
                            log_data["message"] = " " + current_message.strip()
                        else:
                            # Остальные строки многострочного сообщения - с timestamp
                            log_data["timestamp"] = last_timestamp
                            log_data["level"] = last_level
                    else:
                        # Обновляем последние значения
                        last_timestamp = current_timestamp
                        last_level = current_level

                    # Форматируем строку лога
                    formatted_line = format_log_line(log_data, show_timestamp=True)
                    if formatted_line is not None:
                        # В режиме follow выводим сразу для реального времени
                        if follow:
                            console.print(formatted_line)
                        else:
                            # В обычном режиме накапливаем в буфере для правильного порядка
                            log_buffer.append(formatted_line)

                        line_count += 1

                    # Ограничение количества строк (только для обычных логов)
                    if lines and line_count >= lines:
                        if not follow:
                            # В обычном режиме выходим после показа нужного количества строк
                            break
                        else:
                            # В режиме follow показываем последние N записей, затем продолжаем следить
                            if line_count == lines:
                                # Сбрасываем счетчики для новых записей (без вывода сообщения)
                                line_count = 0
                                ping_count = 0

                    # Небольшая задержка для читаемости (только в обычном режиме)
                    if not follow:
                        time.sleep(0.01)

                # Защита от зависания: если обработано много строк, но не найдено логов с нужным уровнем
                if (
                        not follow
                        and level_filter
                        and processed_count > 1000
                        and line_count == 0
                ):
                    console.print(
                        f"[yellow]Не найдено логов с уровнем {level_filter} среди {processed_count} обработанных записей[/yellow]"
                    )
                    break

                # Дополнительная защита: если запрашивается определенное количество строк, но их нет
                if (
                        not follow
                        and lines
                        and processed_count > lines * 10
                        and line_count == 0
                ):
                    console.print(
                        f"[yellow]Не найдено логов среди {processed_count} обработанных записей[/yellow]"
                    )
                    break

        except KeyboardInterrupt:
            pass

        finally:
            # В обычном режиме выводим накопленные логи из буфера
            if not follow and log_buffer:
                # Сортируем логи по timestamp для правильного порядка
                def extract_timestamp(log_item):
                    # Извлекаем timestamp из Rich Text объекта
                    try:
                        text_str = str(log_item)
                        # Ищем timestamp в формате [timestamp] (первое вхождение)
                        import re

                        timestamp_match = re.search(r"\[([^\]]+)\]", text_str)
                        if timestamp_match:
                            timestamp = timestamp_match.group(1)
                            # Преобразуем timestamp в формат для сортировки
                            # Формат: 05.10.25 20:31:19.819
                            try:
                                # Убираем точки из даты и двоеточия из времени для сортировки
                                clean_timestamp = (
                                    timestamp.replace(".", "")
                                    .replace(":", "")
                                    .replace(" ", "")
                                )
                                return clean_timestamp
                            except:
                                return timestamp
                    except:
                        pass
                    return "00000000000000000"  # Возвращаем минимальное значение для сортировки

                # Сортируем логи по timestamp
                try:
                    log_buffer.sort(key=extract_timestamp)
                except Exception:
                    # Если сортировка не удалась, выводим как есть
                    pass

                for formatted_line in log_buffer:
                    console.print(formatted_line)

            response.close()

    except Exception as e:
        # Пробрасываем исключение для обработки в вызывающем коде
        raise


@click.command()
@click.argument("component_name")
@click.option("--browser", "-b", is_flag=True, help="Открыть логи в браузере")
@click.option(
    "--follow", "-f", is_flag=True, help="Следить за логами в реальном времени"
)
@click.option(
    "--lines",
    "-n",
    type=int,
    help="Количество строк логов (по умолчанию: 50, или все при --follow)",
)
@click.option(
    "--tail",
    "-t",
    type=int,
    help="Количество последних записей для показа (по умолчанию: 10 в режиме follow, 50 в обычном режиме)",
)
@click.option("--no-cache", is_flag=True, help="Отключить кэширование")
@click.option("--no-headers", is_flag=True, help="Не показывать заголовок консоли")
@click.option("--verbose", "-v", is_flag=True, help="Подробный вывод HTTP запросов")
@click.pass_context
def logs(
        ctx,
        component_name,
        browser,
        follow,
        lines,
        tail,
        no_cache,
        no_headers,
        verbose,
):
    """Просмотр логов компонентов"""
    try:
        # Создаем API клиент с нужными параметрами
        api = _get_api_client(verbose=verbose, ctx=ctx)

        # Показываем заголовок консоли
        show_console_header(api, show_header=not no_headers)

        # Используем callback для прогресс-бара
        from core.progress import create_progress_context

        with create_progress_context(
                f"Поиск компонента {component_name}...",
        ) as progress_callback:
            # Используем существующий метод с callback
            component_id = api.find_component_id_by_name(
                component_name,
                no_cache=no_cache,
                progress=progress_callback,
            )
            if component_id:
                component_info = {"id": component_id, "name": component_name}
            else:
                component_info = None

        if not component_info:
            console.print(f"[red]Компонент {component_name} не найден в кэше[/red]")
            console.print("[yellow]Доступные компоненты:[/yellow]")

            # Показываем доступные компоненты из кэша или загружаем заново
            try:
                components = api.get_components()
                for group in components:
                    namespace = group.get("namespace", "Unknown")
                    stacks = group.get("stacks", [])
                    for stack in stacks:
                        stack_components = stack.get("components", [])
                        for comp in stack_components:
                            comp_name = comp.get("name", "Unknown")
                            console.print(f"  - {comp_name} (namespace: {namespace})")
            except Exception as e:
                console.print(
                    f"[dim]Не удалось загрузить список компонентов: {e}[/dim]"
                )
            return

        # Получаем ID компонента
        component_id = component_info.get("id")
        if not component_id:
            console.print(
                f"[red]Не удалось получить ID компонента {component_name}[/red]"
            )
            return

        console.print(
            f"[green]Найден компонент: {component_name} (ID: {component_id})[/green]"
        )

        # Если нужно открыть в браузере
        if browser:
            logview_url = f"{api.base_url}/logview/{component_id}"
            console.print(f"[blue]Открываем логи в браузере: {logview_url}[/blue]")
            webbrowser.open(logview_url)
            return

        # Настройка параметров
        if tail is not None:
            # Если указан --tail, используем его значение
            lines = tail
        elif lines is None:
            if follow:
                lines = 50  # В режиме follow показываем последние 50 записей
            else:
                lines = 50  # Обычный режим - показываем 50 записей

        # Если не указан --follow, работаем в обычном режиме (не follow)
        if not follow:
            follow = False

        # Потоковое чтение логов с обработкой ошибок кеша
        try:
            stream_logs(
                api, component_id, lines=lines, follow=follow, level_filter=None
            )
        except Exception as e:
            error_msg = str(e)
            # Перехватываем любые ошибки при получении логов (включая timeout)
            if (
                    "There is no container, service or task with ID" in error_msg
                    or "Read timed out" in error_msg
                    or "Connection" in error_msg
            ):
                console.print(
                    f"[yellow]Task ID {component_id} не найден, обновляем кеш...[/yellow]"
                )

                # Инвалидируем кеш для этого компонента
                cache_key = f"component_info:{component_name}"
                if api.cache:
                    api.cache.invalidate(cache_key)
                    console.print(f"[dim]Кеш для {component_name} инвалидирован[/dim]")

                # Получаем свежую информацию о компоненте
                console.print(
                    f"[blue]Повторный поиск компонента {component_name}...[/blue]"
                )
                component_info = get_component_info(
                    api, component_name, no_cache=True
                )

                if not component_info:
                    console.print(
                        f"[red]Компонент {component_name} не найден после обновления кеша[/red]"
                    )
                    return

                # Получаем новый ID компонента
                new_component_id = component_info.get("id")

                if not new_component_id:
                    console.print(
                        f"[red]Не удалось получить новый ID компонента {component_name}[/red]"
                    )
                    return

                console.print(
                    f"[green]Найден компонент: {component_name} (ID: {new_component_id})[/green]"
                )

                # Повторяем попытку с новым ID
                stream_logs(
                    api,
                    new_component_id,
                    lines=lines,
                    follow=follow,
                    level_filter=level,
                )
            else:
                # Если это другая ошибка, просто пробрасываем её
                raise

    except ImagenariumAPIError as e:
        console.print(f"[red]Ошибка API: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Ошибка: {e}[/red]")
        raise click.Abort()
