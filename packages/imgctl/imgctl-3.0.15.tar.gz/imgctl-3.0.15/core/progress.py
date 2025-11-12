"""
Утилиты для отображения прогресса выполнения запросов
"""
from contextlib import contextmanager
from typing import Protocol, Optional


class ProgressCallback(Protocol):
    """Протокол для callback'ов отображения прогресса"""

    def on_request_start(self, description: str) -> None:
        """Вызывается при начале реального сетевого запроса"""
        ...

    def on_request_end(self) -> None:
        """Вызывается при завершении реального сетевого запроса"""
        ...


class NullProgressCallback:
    """Callback, который ничего не делает (по умолчанию)"""

    def __init__(self):
        """Инициализация пустого callback"""
        pass

    def on_request_start(self, description: str) -> None:
        """Ничего не делает"""
        pass

    def on_request_end(self) -> None:
        """Ничего не делает"""
        pass


class RichProgressCallback:
    """Callback для отображения прогресса через Rich"""

    def __init__(self, console, progress, task_id: Optional[int] = None, step_info: Optional[str] = None):
        """
        Args:
            console: Rich Console
            progress: Rich Progress объект
            task_id: ID задачи прогресс-бара (если None, будет создан автоматически)
            step_info: Информация о шаге (например, "1/3") для добавления в описание
        """
        self.console = console
        self.progress = progress
        self.task_id = task_id
        self._auto_task_id = None
        self.step_info = step_info

    def on_request_start(self, description: str) -> None:
        """Создает или обновляет задачу прогресс-бара"""
        # Добавляем информацию о шаге если есть
        if self.step_info:
            description = f"{description} ({self.step_info})"

        if self.task_id is None:
            # Автоматически создаем задачу если не указан ID
            if self._auto_task_id is None:
                self._auto_task_id = self.progress.add_task(description, total=None)
            else:
                self.progress.update(self._auto_task_id, description=description)
        else:
            self.progress.update(self.task_id, description=description)

    def on_request_end(self) -> None:
        """Завершает задачу прогресс-бара"""
        task_id = self.task_id or self._auto_task_id
        if task_id is not None:
            # Не удаляем задачу, просто обновляем описание
            self.progress.update(task_id, description="Обработка данных...")


@contextmanager
def create_progress_context(description: str):
    """
    Context manager для создания прогресс-бара через Rich

    Callback автоматически вызывается только при реальных сетевых запросах,
    а не при данных из кеша. Progress создается только когда callback действительно вызывается.

    Args:
        description: Описание операции (используется при первом реальном запросе)

    Yields:
        ProgressCallback для использования в сервисах
    """
    # Создаем ленивый callback, который создаст Progress только при первом вызове
    from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
    from rich.console import Console

    console = Console()
    progress_obj = None
    task_id = None

    class LazyProgressCallback:
        """Callback, который создает Progress только при первом использовании"""

        def on_request_start(self, desc: str) -> None:
            nonlocal progress_obj, task_id
            if progress_obj is None:
                # Создаем Progress только при первом реальном запросе
                progress_obj = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    TimeElapsedColumn(),
                    console=console,
                    transient=True,
                )
                progress_obj.__enter__()
                task_id = progress_obj.add_task(description, total=None)
            else:
                # Обновляем описание если уже создан
                progress_obj.update(task_id, description=desc)

        def on_request_end(self) -> None:
            nonlocal progress_obj, task_id
            if progress_obj is not None and task_id is not None:
                progress_obj.update(task_id, description="Обработка данных...")

    callback = LazyProgressCallback()

    try:
        yield callback
    finally:
        # Закрываем Progress если был создан
        if progress_obj is not None:
            try:
                progress_obj.__exit__(None, None, None)
            except Exception:
                pass
