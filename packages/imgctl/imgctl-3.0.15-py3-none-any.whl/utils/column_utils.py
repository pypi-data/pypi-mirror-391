"""
Утилиты для работы с именами столбцов
"""


def snake_to_upper(column_name: str) -> str:
    """
    Преобразует имя столбца из snake_case в UPPER_CASE

    Args:
        column_name: Имя столбца в snake_case (например, 'image_name', 'stack_id')

    Returns:
        Имя столбца в UPPER_CASE (например, 'IMAGE_NAME', 'STACK_ID')
    """
    return column_name.upper()


def normalize_column_name(column_name: str) -> str:
    """
    Нормализует имя столбца для использования в коде (оставляет как есть, если уже snake_case)

    Args:
        column_name: Имя столбца (может быть в UPPER_CASE, camelCase и т.д.)

    Returns:
        Имя столбца в snake_case
    """
    # Если уже в snake_case, возвращаем как есть
    if '_' in column_name and column_name.islower():
        return column_name

    # Если в UPPER_CASE, преобразуем в snake_case
    if column_name.isupper():
        return column_name.lower()

    # Для camelCase и других форматов - простая конвертация
    # TODO: можно добавить более сложную логику конвертации camelCase -> snake_case
    return column_name.lower()


def format_headers_for_display(columns: list[str]) -> dict[str, str]:
    """
    Создает словарь соответствия snake_case -> UPPER_CASE для заголовков

    Args:
        columns: Список имен столбцов в snake_case

    Returns:
        Словарь {snake_case: UPPER_CASE}
    """
    return {col: snake_to_upper(col) for col in columns}


def convert_row_keys_to_upper(row: dict) -> dict:
    """
    Преобразует ключи словаря из snake_case в UPPER_CASE

    Args:
        row: Словарь с данными (ключи в snake_case)

    Returns:
        Словарь с ключами в UPPER_CASE (для отображения)
    """
    result = {}
    for key, value in row.items():
        # Для динамических столбцов (ENV.*, PARAMS.*) оставляем как есть
        if '.' in key or key.startswith('_'):
            result[key] = value
        else:
            result[snake_to_upper(key)] = value
    return result
