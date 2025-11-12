"""
Утилиты для работы с динамическими столбцами (ENV, PARAMS)
"""

from typing import List, Dict, Any


def normalize_column_name(column_name: str, all_columns: List[str]) -> str:
    """
    Нормализует имя столбца: принимает UPPER_CASE от пользователя, возвращает snake_case для использования в коде

    Args:
        column_name: Имя столбца от пользователя (может быть в UPPER_CASE или snake_case)
        all_columns: Список всех доступных столбцов (в snake_case или с сохранением регистра для динамических)

    Returns:
        Нормализованное имя столбца для использования в коде
    """
    # Преобразуем входное имя в lowercase для поиска
    column_lower = column_name.lower()

    # Для динамических столбцов (env.*, params.*) проверяем разные варианты регистра
    if column_lower.startswith("env.") or column_lower.startswith("params."):
        # Сначала проверяем точное совпадение (в исходном регистре)
        if column_name in all_columns:
            return column_name
        # Затем проверяем lowercase версию
        if column_name.lower() in all_columns:
            return column_name.lower()
        # Если не найдено, ищем колонку с нечувствительным к регистру сравнением
        # (динамические колонки могут быть с любым регистром ключа)
        prefix = column_lower.split(".", 1)[0] + "."  # "params." или "env."
        suffix = column_name.split(".", 1)[1] if "." in column_name else ""  # "CLIENT_PORT"
        suffix_lower = suffix.lower()  # "client_port"

        # Ищем колонку с тем же префиксом и суффиксом (нечувствительно к регистру)
        for col in all_columns:
            col_lower = col.lower()
            if col_lower.startswith(prefix):
                col_suffix = col.split(".", 1)[1] if "." in col else ""
                # Сравниваем суффиксы нечувствительно к регистру
                if col_suffix.lower() == suffix_lower:
                    return col

        # Если ничего не найдено, возвращаем lowercase версию
        return column_name.lower()
    else:
        # Для остальных столбцов: ищем в snake_case (все столбцы теперь в snake_case)
        if column_lower in all_columns:
            return column_lower
        # Если не найден, возвращаем lowercase версию
        return column_lower


def parse_columns_with_env_support(
        columns_spec: str, default_columns: List[str], all_columns: List[str]
) -> List[str]:
    """
    Парсит спецификацию столбцов с поддержкой ENV столбцов

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
                column_spec = part[1:]
                column = normalize_column_name(column_spec, all_columns)
                if column in all_columns and column not in result_columns:
                    result_columns.append(column)
            elif part.startswith("-"):
                # Удаляем столбец
                column_spec = part[1:]
                column = normalize_column_name(column_spec, all_columns)
                if column in result_columns:
                    result_columns.remove(column)
            else:
                # Обычный столбец (без префикса) - заменяем весь список
                result = []
                for p in parts:
                    column = normalize_column_name(p, all_columns)
                    if column in all_columns:
                        result.append(column)
                return result

        return result_columns
    else:
        # Обычный режим: явное указание столбцов
        result = []
        for part in parts:
            column = normalize_column_name(part, all_columns)
            if column in all_columns:
                result.append(column)

        return result


def parse_filters_with_env_support(filters: List[str]) -> List[Dict[str, Any]]:
    """
    Парсит список фильтров с поддержкой ENV столбцов

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

        column_spec = parts[0].strip()
        # Преобразуем имя столбца (принимаем UPPER_CASE от пользователя)
        # Для динамических колонок (env.*, params.*) нормализуем без списка all_columns
        # так как они могут быть в любом регистре в данных
        if column_spec.lower().startswith(('env.', 'params.')):
            # Для env.* и params.* сохраняем структуру, но нормализуем регистр префикса
            # Суффикс (имя ключа) может быть в любом регистре в данных
            parts_col = column_spec.split('.', 1)
            if len(parts_col) == 2:
                prefix = parts_col[0].lower()  # "env" или "params"
                suffix = parts_col[1]  # "CLIENT_PORT" - сохраняем исходный регистр
                column = f"{prefix}.{suffix}"
            else:
                column = column_spec.lower()
        else:
            # Для остальных колонок используем lowercase
            column = column_spec.lower()
        value = parts[1].strip()

        # Убираем кавычки если есть
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

        parsed_filters.append({"column": column, "operator": operator, "value": value})

    return parsed_filters


def convert_params_filters_to_raw(
        filters: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Преобразует фильтры PARAMS в фильтры по исходным значениям (до маскирования)

    Args:
        filters: Список фильтров

    Returns:
        Список фильтров с преобразованными именами столбцов
    """
    converted_filters = []

    for filter_item in filters:
        column = filter_item["column"]

        # Если это фильтр по params.<параметр>, заменяем на params.<параметр>_raw
        if column.startswith("params.") and not column.endswith("_raw"):
            # Проверяем, есть ли соответствующий _raw столбец
            raw_column = column + "_raw"
            converted_filters.append(
                {
                    "column": raw_column,
                    "operator": filter_item["operator"],
                    "value": filter_item["value"],
                }
            )
        else:
            # Оставляем фильтр как есть
            converted_filters.append(filter_item)

    return converted_filters


def convert_env_filters_to_raw(filters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Преобразует фильтры ENV в фильтры по исходным значениям (до маскирования)

    Args:
        filters: Список фильтров

    Returns:
        Список фильтров с преобразованными именами столбцов
    """
    converted_filters = []

    for filter_item in filters:
        column = filter_item["column"]

        # Если это фильтр по env.<переменная>, заменяем на env.<переменная>_raw
        if column.startswith("env.") and not column.endswith("_raw"):
            # Проверяем, есть ли соответствующий _raw столбец
            raw_column = column + "_raw"
            converted_filters.append(
                {
                    "column": raw_column,
                    "operator": filter_item["operator"],
                    "value": filter_item["value"],
                }
            )
        else:
            # Оставляем фильтр как есть
            converted_filters.append(filter_item)

    return converted_filters
