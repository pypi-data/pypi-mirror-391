"""
Модуль для единого управления verbose режимом
"""

import sys

# Глобальный флаг verbose режима
_verbose_enabled = False


def verbose_print(message: str):
    """Выводит сообщение только если включен verbose режим"""
    if _verbose_enabled:
        print(f'[DEBUG] {message}', file=sys.stderr, flush=True)


def is_verbose_enabled():
    """Возвращает True если verbose режим включен"""
    return _verbose_enabled


def set_verbose(enabled: bool):
    """Устанавливает verbose режим"""
    global _verbose_enabled
    _verbose_enabled = enabled

