"""
Валидаторы для входных данных
"""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    """
    Валидирует URL

    Args:
        url: URL для валидации

    Returns:
        True если URL валидный, False иначе
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_namespace(namespace: str) -> bool:
    """
    Валидирует namespace

    Args:
        namespace: Namespace для валидации

    Returns:
        True если namespace валидный, False иначе
    """
    if not namespace:
        return False

    # Namespace должен содержать только буквы, цифры, дефисы и подчеркивания
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, namespace))


def validate_stack_id(stack_id: str) -> bool:
    """
    Валидирует stack ID

    Args:
        stack_id: Stack ID для валидации

    Returns:
        True если stack ID валидный, False иначе
    """
    if not stack_id:
        return False

    # Stack ID должен содержать только буквы, цифры, дефисы и подчеркивания
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, stack_id))


def validate_version(version: str) -> bool:
    """
    Валидирует версию

    Args:
        version: Версия для валидации

    Returns:
        True если версия валидная, False иначе
    """
    if not version:
        return False

    # Простая валидация версии (можно расширить)
    pattern = r"^[a-zA-Z0-9._-]+$"
    return bool(re.match(pattern, version))


def validate_git_ref(git_ref: str) -> bool:
    """
    Валидирует git ref

    Args:
        git_ref: Git ref для валидации

    Returns:
        True если git ref валидный, False иначе
    """
    if not git_ref:
        return False

    # Git ref может содержать буквы, цифры, дефисы, подчеркивания, слеши и точки
    pattern = r"^[a-zA-Z0-9._/-]+$"
    return bool(re.match(pattern, git_ref))
