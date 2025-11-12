"""
Класс для подсветки статусов, имен компонентов и других значений с цветовым кодированием
"""

from typing import Any


class Highlighter:
    """Класс для стилизации статусов и значений статусов с Rich markup"""

    # Значения для зеленого цвета (успешные/рабочие)
    SUCCESS = {
        "RUNNING", "ACTIVE", "READY", "HEALTHY", "DEPLOYED", "AVAILABLE"
    }

    # Значения для красного цвета (ошибки/остановленные)
    ERROR = {
        "STOPPED", "INACTIVE", "TERMINATED", "FAILED", "ERROR",
        "OFF", "CANCELED", "UNHEALTHY", "DOWN", "DRAIN", "DRAINING", "UNAVAILABLE"
    }

    # Значения для желтого цвета (ожидание/предупреждение)
    WARNING = {
        "PENDING", "WAITING", "STARTING", "BROKEN", "PAUSE", "PAUSED"
    }

    @classmethod
    def highlight(cls, value: str, check_partial: bool = True, preserve_markup: bool = True) -> str:
        """
        Подсвечивает значение статуса или доступности цветом

        Args:
            value: Значение для подсветки
            check_partial: Если True, проверяет частичные статусы (PARTIAL_*).
                          По умолчанию True для статусов, False для availability
            preserve_markup: Если True, не перезаписывает существующий Rich markup

        Returns:
            Строка с Rich markup
        """
        if not value:
            return value

        # Проверяем, есть ли уже Rich markup
        if preserve_markup and "[" in value and "]" in value:
            return value

        value_upper = value.upper()

        # Частичные статусы (например, PARTIAL_RUNNING) - только для статусов
        if check_partial and value_upper.startswith("PARTIAL"):
            return f"[bold orange3]{value}[/bold orange3]"

        # Успешные значения
        if value_upper in cls.SUCCESS:
            return f"[bold green]{value}[/bold green]"

        # Ошибочные значения
        if value_upper in cls.ERROR:
            return f"[bold red]{value}[/bold red]"

        # Предупреждающие значения
        if value_upper in cls.WARNING:
            return f"[bold yellow]{value}[/bold yellow]"

        # По умолчанию без стилизации
        return value

    @classmethod
    def highlight_component_name(cls, name: str, namespace: str) -> str:
        """
        Подсвечивает имя компонента: все что до namespace обычным белым, namespace серым

        Args:
            name: Имя компонента (может содержать Rich markup от фильтров, который будет удален)
            namespace: Namespace компонента

        Returns:
            Строка с Rich markup
        """
        import re

        # Убираем существующий Rich markup для поиска
        clean_name = re.sub(r'\[[^\]]*\]', '', name)

        if "-" in clean_name and namespace:
            # Ищем namespace в конце имени компонента
            namespace_suffix = f"-{namespace}"
            if clean_name.endswith(namespace_suffix):
                component_part = clean_name[: -len(namespace_suffix)]
                namespace_part = namespace_suffix
                # Просто применяем подсветку к чистому тексту
                return f"{component_part}[dim]{namespace_part}[/dim]"
            else:
                # Если namespace не найден в конце, ищем его в середине
                # Например: oms-suzlet-suz5 с namespace suzlet-suz5
                if namespace in clean_name:
                    # Находим позицию namespace в имени
                    namespace_pos = clean_name.find(namespace)
                    if namespace_pos > 0 and clean_name[namespace_pos - 1] == "-":
                        # Namespace найден после дефиса
                        component_part = clean_name[: namespace_pos - 1]
                        namespace_part = clean_name[namespace_pos - 1:]
                        return f"{component_part}[dim]{namespace_part}[/dim]"

        return clean_name

    @classmethod
    def highlight_tag(cls, tag: str) -> str:
        """
        Подсвечивает тег: строка до __ жирным белым, остальное обычным белым

        Args:
            tag: Тег для подсветки

        Returns:
            Строка с Rich markup
        """
        if "__" in tag:
            # Разделяем на часть до __ и после
            parts = tag.split("__", 1)
            if len(parts) == 2:
                before_part = parts[0]
                after_part = "__" + parts[1]
                return f"[bold white]{before_part}[/bold white][white]{after_part}[/white]"

        return tag

    @classmethod
    def highlight_value(cls, value: Any) -> str:
        """
        Форматирует значение с выделением пробелов в начале/конце красным цветом
        Используется для переменных окружения и параметров стеков

        Args:
            value: Значение для форматирования

        Returns:
            Строка с Rich markup, где пробелы в начале/конце выделены красным
        """

        # Если значение не строка, применяем форматирование по типу
        if not isinstance(value, str):
            # Boolean значения - yellow
            if isinstance(value, bool):
                return f"[yellow]{str(value).lower()}[/yellow]"

            # Числа - cyan
            if isinstance(value, (int, float)):
                return f"[cyan]{value}[/cyan]"

            return str(value)

        str_value = str(value)

        # Проверяем начальные и конечные пробелы
        leading_spaces = len(str_value) - len(str_value.lstrip())
        trailing_spaces = len(str_value) - len(str_value.rstrip())

        if leading_spaces > 0 or trailing_spaces > 0:
            # Разделяем на части: начальные пробелы, основной текст, конечные пробелы
            main_part = str_value.strip()
            leading_part = str_value[:leading_spaces]
            trailing_part = str_value[-trailing_spaces:] if trailing_spaces > 0 else ""

            # Форматируем основной текст по типу
            formatted_main = cls._highlight_value(main_part)

            # Собираем результат с красными пробелами (красный фон с белым текстом для лучшей видимости)
            result = f"[bold white on red]{leading_part}[/bold white on red]"
            result += formatted_main
            if trailing_part:
                result += f"[bold white on red]{trailing_part}[/bold white on red]"

            return result

        # Если пробелов нет, применяем форматирование по типу
        return cls._highlight_value(str_value)

    @classmethod
    def _highlight_value(cls, str_value: str) -> str:
        """
        Вспомогательный метод для форматирования содержимого значения по типу
        """
        import re

        str_lower = str_value.strip().lower()

        # Проверяем boolean значения в строках (true/false, y/n)
        if str_lower in ("true", "false", "y", "n"):
            return f"[yellow]{str_value}[/yellow]"

        # Проверяем, является ли строка URL/ссылкой
        url_pattern = re.compile(
            r'^https?://'  # http:// или https://
            r'[^\s/$.?#].[^\s]*$',  # остальная часть URL
            re.IGNORECASE
        )

        if url_pattern.match(str_value.strip()):
            # Ссылки - cyan
            return f"[cyan]{str_value}[/cyan]"

        # Все остальное (строки) - без раскраски
        return str_value
