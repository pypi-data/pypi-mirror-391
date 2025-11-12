"""
Форматтеры для вывода данных
"""

import json
import os
import re
import shutil
from typing import Any, Dict, List, Optional, Callable

import yaml
from rich.console import Console
from rich.table import Table

# Создаем Console с параметрами для совместимости с различными терминалами
console = Console(
    force_terminal=True,
    legacy_windows=False,
    color_system="truecolor",  # Расширенный набор цветов (24-битная палитра)
)


def display_console_header(
        console_name: str, console_color: str = "#ffffff", version: str = None
) -> None:
    """
    Отображает заголовок консоли во всю ширину терминала с заливкой цветом

    Args:
        console_name: Название консоли
        console_color: Цвет фона в формате HEX (например, "#2d8080")
        version: Версия системы (опционально)
    """
    try:
        # Получаем ширину терминала
        terminal_width = shutil.get_terminal_size().columns

        # Создаем текст заголовка слева
        left_text = f" ᪣ Imagenarium: {console_name}"

        # Создаем текст версии справа (если есть)
        right_text = f"v{version} " if version else ""

        # Вычисляем отступы
        if right_text:
            # Есть версия - размещаем слева и справа
            padding_needed = terminal_width - len(left_text) - len(right_text)
            if padding_needed > 0:
                middle_padding = " " * padding_needed
                full_line = left_text + middle_padding + right_text
            else:
                # Не помещается - показываем только левую часть
                full_line = left_text + " " * (terminal_width - len(left_text))
        else:
            # Нет версии - только левая часть
            padding_needed = terminal_width - len(left_text)
            full_line = left_text + " " * padding_needed

        # Определяем цвет текста в зависимости от текущего фона терминала
        def get_adaptive_text_color():
            """Определяет оптимальный цвет текста для текущего фона терминала"""
            try:
                # Проверяем переменную окружения TERM для определения типа терминала
                term = os.environ.get("TERM", "").lower()

                # Проверяем, поддерживает ли Rich цвета в текущем окружении
                # В контейнерах или при отсутствии терминала используем белый
                if not term or term in ["dumb", "unknown"]:
                    # В контейнерах обычно лучше использовать белый текст
                    return "white"
                # Для темных терминалов (iTerm2, Terminal.app в темной теме)
                if any(
                        dark_term in term
                        for dark_term in ["iterm", "xterm-256color", "screen-256color"]
                ):
                    # Проверяем переменные окружения для темной темы
                    if os.environ.get("ITERM_PROFILE", "").lower() in [
                        "dark",
                        "midnight",
                    ]:
                        return "white"
                    # Проверяем цветовую схему macOS Terminal
                    if os.environ.get("COLORFGBG", "").endswith(";0"):  # темный фон
                        return "white"

                # Проверяем настройки Rich Console
                if hasattr(console, "color_system") and console.color_system:
                    # Если Rich определяет ограниченную цветовую систему
                    if console.color_system == "standard" and term in [
                        "dumb",
                        "unknown",
                    ]:
                        return "white"  # Для простых терминалов используем белый
                    elif console.color_system in ["256", "truecolor"]:
                        # Для продвинутых терминалов проверяем переменные окружения
                        if os.environ.get("ITERM_PROFILE", "").lower() in [
                            "dark",
                            "midnight",
                        ]:
                            return "white"
                        elif os.environ.get("COLORFGBG", "").endswith(";0"):
                            return "white"
                        else:
                            return "black"
                    elif not console.color_system or console.color_system == "none":
                        # Если цвета не поддерживаются, используем белый
                        return "white"

                # Для светлых терминалов или по умолчанию
                # Но если TERM не определен или пустой, используем белый (контейнеры)
                return "black" if term else "white"

            except Exception:
                # Fallback: белый текст (лучше виден на любом фоне)
                return "white"

        # Получаем адаптивный цвет текста
        text_color = get_adaptive_text_color()

        # Проверяем возможности терминала
        term = os.environ.get("TERM", "").lower()
        is_container = not term or term in ["dumb", "unknown"] or os.path.exists("/.dockerenv")

        # Проверяем реальные возможности Rich Console
        # В контейнерах часто проблемы с отображением фоновых цветов
        # Используем простой белый/яркий белый текст без фона для надежности
        if is_container:
            # В контейнерах используем простой яркий белый текст без фона
            console.print(f"[bold bright_white]{full_line}[/bold bright_white]")
        else:
            # Используем яркий белый для лучшей видимости
            if text_color == "white":
                style_color = "bright_white"
            else:
                style_color = text_color

            # Выводим заголовок с заливкой цветом (только локально)
            console.print(
                f"[bold {style_color} on {console_color}]{full_line}[/bold {style_color} on {console_color}]"
            )

    except Exception:
        # Fallback: простой вывод без Rich
        fallback_text = f" ᪣ Imagenarium: {console_name}"
        if version:
            fallback_text += f" v{version} "
        console.print(
            f"[bold white on {console_color}]{fallback_text}[/bold white on {console_color}]"
        )


def show_console_header(api_client, show_header: bool = True) -> None:
    """
    Получает конфиг консоли и отображает заголовок

    Args:
        api_client: API клиент для получения конфига
        show_header: Показывать ли заголовок (по умолчанию True)
    """
    # В shell режиме не показываем заголовок для внутренних команд
    # (заголовок уже показан при входе в shell)
    import os
    if os.environ.get("IMGCTL_SHELL_MODE") == "1":
        return

    if not show_header:
        return

    try:
        # Получаем конфиг консоли
        config = api_client.get_console_config()

        console_name = config.get("consoleName", "Imagenarium")
        console_color = config.get("consoleColor", "#ffffff")

        # Получаем версию (с кэшированием)
        try:
            version = api_client.get_version()
        except Exception:
            version = None

        # Отображаем заголовок
        display_console_header(console_name, console_color, version)

    except Exception:
        # Fallback: заголовок по умолчанию
        display_console_header("Imagenarium", "#ffffff")


def parse_columns_spec(
        columns_spec: str, default_columns: List[str], all_columns: List[str]
) -> List[str]:
    """
    Парсит спецификацию столбцов с поддержкой префиксов +/-

    Args:
        columns_spec: Спецификация столбцов (например: "NAME,STATUS" или "+REPLICAS,-NAMESPACE")
        default_columns: Столбцы по умолчанию
        all_columns: Все доступные столбцы

    Returns:
        Список столбцов для отображения
    """
    if not columns_spec:
        return default_columns

    # Разделяем по запятым и убираем пробелы
    parts = [part.strip() for part in columns_spec.split(",")]

    # Проверяем, есть ли префиксы +/-
    has_prefixes = any(part.startswith(("+", "-")) for part in parts)

    if has_prefixes:
        # Режим с префиксами: начинаем с столбцов по умолчанию
        result_columns = default_columns.copy()

        for part in parts:
            if part.startswith("+"):
                # Добавляем столбец
                column = part[1:].upper()
                if column in all_columns and column not in result_columns:
                    result_columns.append(column)
            elif part.startswith("-"):
                # Удаляем столбец
                column = part[1:].upper()
                if column in result_columns:
                    result_columns.remove(column)
            else:
                # Обычный столбец (без префикса) - заменяем весь список
                return [part.upper() for part in parts if part.upper() in all_columns]

        return result_columns
    else:
        # Обычный режим: явное указание столбцов
        return [part.upper() for part in parts if part.upper() in all_columns]


def parse_filters(filters: List[str]) -> List[Dict[str, Any]]:
    """
    Парсит список фильтров в формате "COLUMN=value", "COLUMN!=value", "COLUMN~pattern"

    Args:
        filters: Список строк фильтров

    Returns:
        Список словарей с информацией о фильтрах
    """
    parsed_filters = []

    for filter_str in filters:
        # Поддерживаемые операторы
        operators = ["!=", ">=", "<=", "~", "=", ">", "<"]

        # Находим оператор в строке
        operator = None
        for op in operators:
            if op in filter_str:
                operator = op
                break

        if not operator:
            continue

        # Разделяем на колонку и значение
        parts = filter_str.split(operator, 1)
        if len(parts) != 2:
            continue

        column = parts[0].strip().upper()
        value = parts[1].strip()

        # Убираем кавычки если есть
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

        parsed_filters.append({"column": column, "operator": operator, "value": value})

    return parsed_filters


def apply_filters(
        data: List[Dict[str, Any]], filters: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Применяет фильтры к данным

    Args:
        data: Список словарей с данными
        filters: Список фильтров

    Returns:
        Отфильтрованные данные
    """
    if not filters:
        return data

    filtered_data = []

    for row in data:
        matches = True

        for filter_info in filters:
            column = filter_info["column"]
            operator = filter_info["operator"]
            value = filter_info["value"]

            # Для динамических колонок (params.*, env.*) ищем колонку нечувствительно к регистру
            if column.lower().startswith(("params.", "env.")):
                # Находим правильное имя колонки в строке (с учетом регистра в данных)
                actual_column = None
                column_lower = column.lower()
                prefix = column_lower.split(".", 1)[0] + "."  # "params." или "env."
                suffix = column.split(".", 1)[1] if "." in column else ""  # "CLIENT_PORT"
                suffix_lower = suffix.lower()

                # Ищем колонку с тем же префиксом и суффиксом (нечувствительно к регистру)
                for col_key in row.keys():
                    col_key_lower = col_key.lower()
                    if col_key_lower.startswith(prefix):
                        col_suffix = col_key.split(".", 1)[1] if "." in col_key else ""
                        if col_suffix.lower() == suffix_lower:
                            actual_column = col_key
                            break

                # Если не нашли, пробуем точное совпадение
                if actual_column is None:
                    if column in row:
                        actual_column = column
                    elif column_lower in [k.lower() for k in row.keys()]:
                        # Находим ключ с таким же lowercase
                        for k in row.keys():
                            if k.lower() == column_lower:
                                actual_column = k
                                break
                    else:
                        actual_column = column  # Используем исходное имя (будет пустое значение)
            else:
                actual_column = column

            # Получаем значение из строки
            import re

            # Убираем Rich markup и лишние пробелы
            raw_value = str(row.get(actual_column, ""))
            cell_value = re.sub(
                r"\[[^\]]*\]", "", raw_value
            )  # Убираем Rich markup [green]...[/green]
            cell_value = re.sub(
                r"\s+", " ", cell_value.strip()
            ).lower()  # Убираем лишние пробелы
            filter_value = str(value).strip().lower()

            # Применяем оператор
            if operator == "=":
                if cell_value != filter_value:
                    matches = False
                    break
            elif operator == "!=":
                if cell_value == filter_value:
                    matches = False
                    break
            elif operator == "~":
                try:
                    if not re.search(filter_value, cell_value):
                        matches = False
                        break
                except re.error:
                    # Если регулярное выражение некорректное, используем простой поиск
                    if filter_value not in cell_value:
                        matches = False
                        break
            elif operator == ">":
                try:
                    if not (cell_value > filter_value):
                        matches = False
                        break
                except (ValueError, TypeError):
                    # Для нечисловых значений сравниваем как строки
                    if not (cell_value > filter_value):
                        matches = False
                        break
            elif operator == "<":
                try:
                    if not (cell_value < filter_value):
                        matches = False
                        break
                except (ValueError, TypeError):
                    if not (cell_value < filter_value):
                        matches = False
                        break
            elif operator == ">=":
                try:
                    if not (cell_value >= filter_value):
                        matches = False
                        break
                except (ValueError, TypeError):
                    if not (cell_value >= filter_value):
                        matches = False
                        break
            elif operator == "<=":
                try:
                    if not (cell_value <= filter_value):
                        matches = False
                        break
                except (ValueError, TypeError):
                    if not (cell_value <= filter_value):
                        matches = False
                        break

        if matches:
            filtered_data.append(row)

    return filtered_data


def highlight_matches(text: str, filters: List[Dict[str, str]]) -> str:
    """
    Подсвечивает совпадения в тексте на основе фильтров
    
    Упрощенная логика: убираем все Rich markup теги, подсвечиваем совпадения.
    Цветовое кодирование применяется заново после подсветки фильтров.

    Args:
        text: Исходный текст (может содержать Rich markup)
        filters: Список фильтров для подсветки

    Returns:
        Текст с подсветкой совпадений (без исходного Rich markup)
    """
    if not filters or not text:
        return text

    # Убираем Rich markup из текста для сравнения и подсветки
    clean_text = re.sub(r"\[[^\]]*\]", "", text)

    for filter_item in filters:
        column = filter_item["column"]
        operator = filter_item["operator"]
        value = filter_item["value"]

        # Подсвечиваем только для операторов = и ~
        if operator in ["=", "~"]:
            if operator == "=":
                # Точное совпадение
                if clean_text.lower() == value.lower():
                    text = f"[bold yellow]{clean_text}[/bold yellow]"
            elif operator == "~":
                # Регулярное выражение
                try:
                    # Ищем совпадения в чистом тексте
                    matches = list(re.finditer(value, clean_text, re.IGNORECASE))
                    if matches:
                        # Подсвечиваем совпадения в чистом тексте
                        result = ""
                        last_end = 0
                        for match in matches:
                            result += clean_text[last_end: match.start()]
                            result += f"[bold yellow]{match.group()}[/bold yellow]"
                            last_end = match.end()
                        result += clean_text[last_end:]
                        text = result
                except re.error:
                    # Если регулярное выражение некорректное, используем простой поиск
                    if value.lower() in clean_text.lower():
                        start = clean_text.lower().find(value.lower())
                        if start != -1:
                            end = start + len(value)
                            text = (
                                    clean_text[:start]
                                    + f"[bold yellow]{clean_text[start:end]}[/bold yellow]"
                                    + clean_text[end:]
                            )

    return text


def format_table(
        data: List[Dict[str, Any]],
        columns: Optional[List[str]] = None,
        no_headers: bool = False,
        highlight_filters: Optional[List[Dict[str, str]]] = None,
) -> None:
    """
    Форматирует данные в стиле kubectl (без рамок, с правильным выравниванием)
    Адаптируется к ширине терминала

    Args:
        data: Список словарей с данными
        columns: Список колонок для отображения
        no_headers: Не показывать заголовки колонок таблицы
        highlight_filters: Список фильтров для подсветки совпадений
    """
    if not data:
        console.print("Данные не найдены")
        return

    if columns is None:
        columns = list(data[0].keys())

    # Преобразуем заголовки столбцов из snake_case в UPPER_CASE для отображения
    from utils.column_utils import snake_to_upper
    display_headers = {col: snake_to_upper(col) for col in columns}

    # Получаем ширину терминала
    terminal_width = shutil.get_terminal_size().columns

    # Создаем Rich Table для правильного выравнивания

    table = Table(
        show_header=not no_headers, show_footer=False, show_edge=False, box=None
    )

    # Вычисляем ширину колонок (используем ширину заголовков UPPER_CASE)
    column_widths = {}
    for col in columns:
        # Начинаем с ширины заголовка (если заголовки показываются)
        header_text = display_headers.get(col, col) if not no_headers else ""
        min_width = len(header_text) if not no_headers else 0

        # Проверяем все значения в колонке
        for item in data:
            value = str(item.get(col, ""))
            min_width = max(min_width, len(value))

        column_widths[col] = min_width

    # Вычисляем общую ширину
    total_width = sum(column_widths.values()) + (len(columns) - 1) * 2

    # Если таблица не помещается, ограничиваем ширину колонок
    if total_width > terminal_width:
        available_width = terminal_width - (len(columns) - 1) * 2
        total_content_width = sum(column_widths.values())

        for col in columns:
            proportion = column_widths[col] / total_content_width
            header_text = display_headers.get(col, col) if not no_headers else ""
            column_widths[col] = max(int(available_width * proportion), len(header_text))

    # Добавляем колонки в таблицу
    for col in columns:
        width = column_widths[col]
        header_text = display_headers.get(col, col) if not no_headers else ""
        justify_value = "right" if col.lower() in ["replicas", "age", "restarts", "components"] else "left"

        if no_headers:
            # Для режима без заголовков используем пустую строку как заголовок
            table.add_column("", width=width, justify=justify_value, style="white")
        else:
            table.add_column(
                header_text,
                width=width,
                justify=justify_value,
                style="white",
                header_style="bold white",
            )

    # Добавляем строки данных
    for item in data:
        row = []
        for col in columns:
            value = str(item.get(col, ""))
            width = column_widths[col]

            # Обрезаем длинные значения
            if len(value) > width:
                if width > 3:
                    display_value = value[: width - 3] + "..."
                else:
                    display_value = value[:width]
            else:
                display_value = value

            # Сначала применяем цветовое кодирование для статусов, доступности, тегов и имен компонентов
            from utils.highlighter import Highlighter

            if col.lower() in ["status", "state"]:
                styled_value = Highlighter.highlight(display_value, check_partial=True, preserve_markup=False)
            elif col.lower() == "availability":
                styled_value = Highlighter.highlight(display_value, check_partial=False, preserve_markup=False)
            elif col.lower() == "tag":
                styled_value = Highlighter.highlight_tag(display_value)
            elif col.lower() == "name":
                # Для имени компонента или стека применяем подсветку
                name_value = display_value
                
                # Проверяем, это стек (формат: stack_id@namespace) или компонент (формат: component-namespace)
                if "@" in name_value:
                    # Стек: подсвечиваем namespace после @
                    stack_id, namespace = name_value.split("@", 1)
                    styled_value = f"{stack_id}[dim]@{namespace}[/dim]"
                else:
                    # Компонент: применяем подсветку имени компонента
                    component_name = name_value
                    # Namespace может отсутствовать в item, если не включен в --columns
                    component_namespace = str(item.get("namespace", "")) if "namespace" in item else ""
                    # Если namespace нет, но имя содержит дефисы, пробуем извлечь из имени
                    if not component_namespace and "-" in component_name:
                        # Простая эвристика: если имя заканчивается на -namespace, извлекаем
                        parts = component_name.rsplit("-", 1)
                        if len(parts) == 2:
                            component_namespace = parts[1]
                    styled_value = Highlighter.highlight_component_name(
                        component_name, component_namespace
                    )
            elif col.lower().startswith("env.") or col.lower().startswith("params."):
                # Для колонок env.* и params.* применяем highlight_value для выделения пробелов
                # Используем оригинальное значение (до обрезки) для корректной обработки пробелов
                original_value = str(item.get(col, ""))
                styled_value = Highlighter.highlight_value(original_value)
                # Если значение было обрезано, обрезаем styled_value тоже
                if len(original_value) > width:
                    if width > 3:
                        styled_value = styled_value[: width - 3] + "..."
                    else:
                        styled_value = styled_value[:width]
            else:
                styled_value = display_value

            # Затем подсвечиваем совпадения с фильтрами (убирает все теги, подсвечивает совпадения)
            if highlight_filters:
                # Создаем фильтры для текущего столбца
                # Нормализуем название колонки для сравнения (UPPER_CASE -> snake_case)
                column_filters = []
                for f in highlight_filters:
                    # Нормализуем название колонки из фильтра (UPPER_CASE -> snake_case)
                    filter_col = f["column"].lower()  # PORTS -> ports
                    if filter_col == col:
                        column_filters.append(f)
                if column_filters:
                    # Применяем подсветку фильтров (убирает все теги из styled_value, подсвечивает совпадения)
                    styled_value = highlight_matches(styled_value, column_filters)

            row.append(styled_value)

        table.add_row(*row)

    # Выводим таблицу
    console.print(table)


def _convert_params_to_object(row: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """
    Конвертирует PARAMS или ENV из строки в объект с сохранением регистра ключей

    Args:
        row: Строка данных
        prefix: Префикс для поиска столбцов (PARAMS или ENV)

    Returns:
        Объект с параметрами/переменными окружения
    """
    result = {}

    # Ищем все столбцы с префиксом prefix.
    for key, value in row.items():
        if key.startswith(f"{prefix}."):
            # Извлекаем имя параметра/переменной (сохраняем регистр)
            param_name = key[len(f"{prefix}."):]
            # Убираем _RAW суффикс если есть
            if param_name.endswith("_RAW"):
                param_name = param_name[:-4]
            # Очищаем Rich markup
            if isinstance(value, str):
                clean_value = re.sub(r"\[[^\]]*\]", "", value).strip()
            else:
                clean_value = value
            result[param_name] = clean_value

    # Если не нашли динамические столбцы, но есть строка, парсим её
    if not result and prefix.lower() in row:
        string_value = row[prefix]
        if isinstance(string_value, str) and string_value.strip():
            # Парсим строку вида "KEY1=value1, KEY2=value2"
            pairs = string_value.split(",")
            for pair in pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    result[key.strip()] = value.strip()

    # Также проверяем оригинальный ключ (с заглавными буквами)
    if not result and prefix in row:
        string_value = row[prefix]
        if isinstance(string_value, str) and string_value.strip():
            # Парсим строку вида "KEY1=value1, KEY2=value2"
            pairs = string_value.split(",")
            for pair in pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    result[key.strip()] = value.strip()

    return result


def format_json(data: Any, indent: int = 2) -> None:
    """
    Форматирует данные в JSON

    Args:
        data: Данные для форматирования
        indent: Отступ для JSON
    """
    try:
        # Конвертируем ключи в нижний регистр и очищаем Rich markup
        converted_data = []
        for row in data:
            converted_row = {}
            for key, value in row.items():
                # Пропускаем столбцы вида PARAMS.<ключ> и ENV.<ключ> - они будут в объектах
                if key.startswith("PARAMS.") or key.startswith("ENV."):
                    continue

                # Очищаем Rich markup и конвертируем в нижний регистр
                if isinstance(value, str):
                    clean_value = re.sub(r"\[[^\]]*\]", "", value).strip()
                else:
                    clean_value = value
                converted_row[key.lower()] = clean_value

            # Конвертируем PARAMS в объект с сохранением регистра ключей
            if "params" in converted_row:
                params_obj = _convert_params_to_object(row, "PARAMS")
                if params_obj:
                    converted_row["params"] = params_obj

            # Конвертируем ENV в объект с сохранением регистра ключей
            if "env" in converted_row:
                env_obj = _convert_params_to_object(row, "ENV")
                if env_obj:
                    converted_row["env"] = env_obj

            converted_data.append(converted_row)

        json_str = json.dumps(converted_data, indent=indent, ensure_ascii=False)
        console.print(json_str)
    except Exception as e:
        console.print(f"[red]Ошибка форматирования JSON: {e}[/red]")


def format_yaml(data: Any, default_flow_style: bool = False) -> None:
    """
    Форматирует данные в YAML

    Args:
        data: Данные для форматирования
        default_flow_style: Стиль потока по умолчанию
    """
    try:
        # Конвертируем ключи в нижний регистр и очищаем Rich markup
        converted_data = []
        for row in data:
            converted_row = {}
            for key, value in row.items():
                # Пропускаем столбцы вида PARAMS.<ключ> и ENV.<ключ> - они будут в объектах
                if key.startswith("PARAMS.") or key.startswith("ENV."):
                    continue

                # Очищаем Rich markup и конвертируем в нижний регистр
                if isinstance(value, str):
                    clean_value = re.sub(r"\[[^\]]*\]", "", value).strip()
                else:
                    clean_value = value
                converted_row[key.lower()] = clean_value

            # Конвертируем PARAMS в объект с сохранением регистра ключей
            if "params" in converted_row:
                params_obj = _convert_params_to_object(row, "PARAMS")
                if params_obj:
                    converted_row["params"] = params_obj

            # Конвертируем ENV в объект с сохранением регистра ключей
            if "env" in converted_row:
                env_obj = _convert_params_to_object(row, "ENV")
                if env_obj:
                    converted_row["env"] = env_obj

            converted_data.append(converted_row)

        yaml_str = yaml.dump(
            converted_data,
            default_flow_style=default_flow_style,
            allow_unicode=True,
            sort_keys=False,
        )
        console.print(yaml_str)
    except Exception as e:
        console.print(f"[red]Ошибка форматирования YAML: {e}[/red]")


def format_template(data: List[Dict[str, Any]], template: str) -> None:
    """
    Форматирует данные по шаблону (как в kubectl)

    Args:
        data: Список словарей с данными
        template: Шаблон с плейсхолдерами (например: "{{.NAME}} {{.STATUS}}")
    """
    if not data:
        return

    for row in data:
        # Убираем Rich markup из значений
        clean_row = {}
        for key, value in row.items():
            if isinstance(value, str):
                clean_row[key] = re.sub(r"\[[^\]]*\]", "", value).strip()
            else:
                clean_row[key] = value

        # Заменяем плейсхолдеры в шаблоне
        formatted_line = template
        for key, value in clean_row.items():
            placeholder = f"{{{key}}}"  # {KEY}
            formatted_line = formatted_line.replace(placeholder, str(value))

        # Заменяем \n на реальные переносы строк
        formatted_line = formatted_line.replace("\\n", "\n")

        console.print(formatted_line)


def print_field(
        data: Dict[str, Any],
        field_name: str,
        label: Optional[str] = None,
        default: Any = "",
        skip_empty: bool = True,
        formatter: Optional[Callable[[Any], str]] = None,
) -> None:
    """
    Выводит поле из словаря в форматированном виде

    Args:
        data: Словарь с данными (ключи в snake_case)
        field_name: Имя поля в snake_case
        label: Метка для отображения (если не указана, используется UPPER_CASE из field_name)
        default: Значение по умолчанию если поле отсутствует
        skip_empty: Пропускать вывод если значение пустое/None (по умолчанию True)
        formatter: Функция для форматирования значения перед выводом
    """
    from utils.column_utils import snake_to_upper

    value = data.get(field_name, default)

    # Для булевых значений: всегда показываем если True, или если skip_empty=False
    if isinstance(value, bool):
        if not value and skip_empty:
            return
        display_value = str(value)
    else:
        # Для других типов: проверяем пустое значение
        if skip_empty and (not value or (isinstance(value, str) and not value.strip())):
            return
        display_value = str(value)

    # Применяем форматтер если есть
    if formatter:
        display_value = formatter(value)

    # Определяем метку для отображения
    if label is None:
        # Преобразуем snake_case в UPPER_CASE для заголовка
        label = snake_to_upper(field_name) if '.' not in field_name and not field_name.startswith(
            '_') else field_name.upper()

    console.print(f"[bold white]{label}:[/bold white] {display_value}")


def format_output(
        data: List[Dict[str, Any]], format_spec: str, columns: Optional[List[str]] = None
) -> None:
    """
    Форматирует данные в указанном формате

    Args:
        data: Список словарей с данными
        format_spec: Спецификация формата (json, yaml, tsv, или template с шаблоном)
        columns: Столбцы для TSV (если применимо)
    """
    # Если формат не указан или это table, используем стандартное табличное форматирование
    if not format_spec or format_spec == "table":
        format_table(data, columns=columns)
        return

    # Проверяем, является ли это template форматом (содержит {})
    if "{" in format_spec and "}" in format_spec:
        format_template(data, format_spec)
    elif format_spec == "json":
        format_json(data)
    elif format_spec == "yaml":
        format_yaml(data)
    elif format_spec == "tsv":
        # TSV - это табличный вывод без заголовков колонок
        format_table(data, columns=columns, no_headers=True)
    else:
        console.print(f"[red]Неподдерживаемый формат: {format_spec}[/red]")
        console.print(
            "Доступные форматы: json, yaml, tsv, или template (например: '{NAME} - {STATUS}')"
        )
