"""
Интерактивная оболочка для imgctl (REPL режим)

Предоставляет интерактивный режим работы с imgctl с поддержкой:
- Автодополнения команд
- История команд
- Сохранение контекста между командами
"""

import os
import shlex
import sys
import threading
from pathlib import Path
from typing import List

import click
from rich.console import Console
from rich.markdown import Markdown

# Проверяем доступность prompt-toolkit
try:
    import prompt_toolkit

    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

from core.completion import CompletionManager

console = Console()

# Глобальная переменная для фонового потока
_cache_update_thread = None
_stop_cache_updates = threading.Event()

# Состояние фонового обновления кэша
_cache_update_in_progress = threading.Event()
_cache_update_lock = threading.Lock()


def _get_api_client_from_ctx(ctx, verbose: bool = False):
    """
    Получает API клиент из контекста или создает новый.

    Args:
        ctx: Click контекст
        verbose: Режим подробного вывода

    Returns:
        ImagenariumAPIClient или None
    """
    from cli.main import get_api_client

    # Проверяем, есть ли уже созданный API клиент в контексте
    if ctx and hasattr(ctx, 'obj') and ctx.obj.get('api'):
        return ctx.obj['api']

    # Создаем API клиент из параметров в контексте
    if not ctx or not hasattr(ctx, 'obj'):
        return None

    server = ctx.obj.get('server')
    username = ctx.obj.get('username')
    password = ctx.obj.get('password')
    config = ctx.obj.get('config')

    try:
        return get_api_client(
            verbose=verbose,
            server=server,
            username=username,
            password=password,
            config=config,
        )
    except Exception:
        return None


def create_imgctl_completer(ctx, completion_manager):
    """
    Создает комплетер для imgctl команд используя Click API
    """
    from prompt_toolkit.completion import Completer, Completion, NestedCompleter
    from cli.main import main

    # Получаем список команд из Click динамически
    commands_dict = {}
    for cmd_name, cmd in main.commands.items():
        if hasattr(cmd, 'list_commands'):
            try:
                # Создаем контекст для команды
                with main.make_context('imgctl', [cmd_name]) as sub_ctx:
                    subcommands = cmd.list_commands(sub_ctx)
                    commands_dict[cmd_name] = {sub: None for sub in subcommands}
            except Exception:
                # Fallback: используем get_short_help_str для определения подкоманд
                commands_dict[cmd_name] = None
        else:
            commands_dict[cmd_name] = None

    # Добавляем специальные команды REPL
    commands_dict["exit"] = None
    commands_dict["quit"] = None
    commands_dict["help"] = None
    commands_dict["clear"] = None

    class ImgctlCompleter(Completer):
        """Комплетер для imgctl команд"""

        def __init__(self, completion_manager, commands_dict):
            self.completion_manager = completion_manager
            self.commands_dict = commands_dict
            # Статический completer для команд из Click
            self.static_completer = NestedCompleter.from_nested_dict(commands_dict)
            # Click main для извлечения опций
            from cli.main import main as click_main
            self.click_main = click_main

        def _yield_list(self, items, start_position):
            from prompt_toolkit.completion import Completion

            for it in items:
                yield Completion(it, start_position=start_position)

        def _current_filters_from_words(self, words: List[str]) -> List[str]:
            """Извлекает все уже указанные --filter из аргументов (поддерживает формы с = и через пробел)."""
            result: List[str] = []
            i = 0
            while i < len(words):
                w = words[i]
                if w == "--filter" and i + 1 < len(words):
                    result.append(words[i + 1])
                    i += 2
                    continue
                if w.startswith("--filter="):
                    result.append(w.split("=", 1)[1])
                i += 1
            return result

        def _get_click_options(self, command: str, subcommand: str = "") -> List[str]:
            """Достает список опций из Click для выбранной команды или подкоманды."""
            try:
                cmd_obj = self.click_main.commands.get(command)
                if not cmd_obj:
                    return []

                # Если subcommand пустой и команда - это не группа (нет метода get_command),
                # то это простая команда, берем её напрямую
                if not subcommand and not hasattr(cmd_obj, 'get_command'):
                    # Это простая команда (например, logs)
                    cmd = cmd_obj
                else:
                    # Это группа с подкомандами
                    if not hasattr(cmd_obj, 'get_command'):
                        return []
                    # Создаем контекст для получения команды
                    with self.click_main.make_context('imgctl', [command, subcommand]) as _:
                        cmd = cmd_obj.get_command(_, subcommand) if subcommand else None

                if not cmd or not hasattr(cmd, 'params'):
                    return []
                opts: List[str] = []
                for p in cmd.params:
                    # Только опции (не аргументы)
                    if getattr(p, 'opts', None):
                        opts.extend(p.opts)
                    if getattr(p, 'secondary_opts', None):
                        opts.extend(p.secondary_opts)
                # Уникализируем, длинные опции впереди
                long_opts = sorted([o for o in opts if o.startswith('--')])
                short_opts = sorted([o for o in opts if o.startswith('-') and not o.startswith('--')])
                return long_opts + short_opts
            except Exception:
                return []

        def _complete_columns(self, command: str, fragment: str):
            """Подсказывает столбцы для --columns, учитывает запятые и префиксы +/-."""
            from prompt_toolkit.completion import Completion

            cols = self.completion_manager.get_columns_for_command(command)

            # Определяем текущий сегмент (после последней запятой)
            if "," in fragment:
                prefix_list = fragment.rsplit(",", 1)[0]
                segment = fragment.rsplit(",", 1)[1].lstrip()
                base_prefix = fragment[: -len(segment)]
            else:
                prefix_list = ""
                segment = fragment
                base_prefix = ""

            # Учитываем + или -
            sign = ""
            if segment.startswith("+") or segment.startswith("-"):
                sign = segment[0]
                segment = segment[1:]

            start_pos = -len(segment) - (1 if sign else 0)

            from utils.column_utils import snake_to_upper
            for c in cols:
                # Преобразуем snake_case в UPPER_CASE для пользователя
                display_col = snake_to_upper(c) if '.' not in c and not c.startswith('_') else c.upper()
                # Сравниваем в верхнем регистре для корректного поиска ENV.* и env.*
                segment_upper = segment.upper()
                display_col_upper = display_col.upper()
                c_upper = c.upper()
                if display_col_upper.startswith(segment_upper) or c_upper.startswith(segment_upper):
                    yield Completion(sign + display_col, start_position=start_pos)

        def _complete_filter(self, command: str, current_text: str, words: List[str]):
            """Комплишн для --filter. Учитывает формы --filter=..., --filter ... и оператор."""
            from prompt_toolkit.completion import Completion
            word_before_cursor = current_text

            # Определяем часть после --filter(=)?
            if word_before_cursor.startswith("--filter="):
                expr = word_before_cursor.split("=", 1)[1]
                start_pos = -len(expr)
            elif word_before_cursor == "--filter":
                expr = ""
                start_pos = 0
            else:
                # Если это значение после --filter через пробел
                expr = word_before_cursor
                start_pos = -len(expr)

            # Если нет оператора — подсказываем имена столбцов
            operators = ["!=", ">=", "<=", "~", "=", ">", "<"]
            op_found = None
            for op in operators:
                if op in expr:
                    op_found = op
                    break

            current_filters = self._current_filters_from_words(words)
            # Исключаем текущий редактируемый фильтр, чтобы не сужать выдачу значений
            try:
                if len(words) >= 3 and words[-2] == "--filter":
                    # форма: --filter VALUE
                    if words[-1] in current_filters:
                        current_filters.remove(words[-1])
                else:
                    # форма: ... --filter=VALUE ...
                    for w in words:
                        if w.startswith("--filter="):
                            val = w.split("=", 1)[1]
                            if val == expr and val in current_filters:
                                current_filters.remove(val)
                            break
            except Exception:
                pass

            if not op_found:
                from utils.column_utils import snake_to_upper
                cols = self.completion_manager.get_columns_for_command(command)  # В snake_case
                # Добавляем динамические префиксы для удобства
                # (env., params.) уже есть в cols при необходимости
                prefix = expr.strip()
                for c in cols:
                    # Преобразуем snake_case в UPPER_CASE для пользователя
                    display_col = snake_to_upper(c) if '.' not in c and not c.startswith('_') else c.upper()
                    if not prefix or display_col.upper().startswith(prefix.upper()):
                        yield Completion(display_col, start_position=start_pos)
                return

            # Есть оператор — подсказываем значения для указанной колонки
            col, value_prefix = expr.split(op_found, 1)
            col = col.strip().lower()  # Преобразуем в snake_case для поиска в данных
            value_prefix = value_prefix.strip()

            # Значения берем по *_RAW при наличии для корректности
            values = self.completion_manager.get_column_values(
                command=command,
                column=col,
                current_filters=current_filters,
                operator=op_found,
                prefix=value_prefix,
            )
            for v in values:
                yield Completion(v, start_position=-len(value_prefix))

        def get_completions(self, document, complete_event):
            text = document.text_before_cursor
            words = text.split()
            # Проверяем, заканчивается ли текст пробелом (курсор после пробела)
            ends_with_space = text.rstrip() != text

            # Для команд с аргументами пытаемся получить динамические completions
            command = words[0] if words else ""

            # Если это первое слово (команда еще не начата), используем статический completer
            if not command:
                for item in self.static_completer.get_completions(document, complete_event):
                    yield item
                return

            # components команды
            if command == "components":
                if len(words) >= 2 and words[1] == "list":
                    # components list → опции и умный комплишн для --columns/--filter
                    word_before_cursor = document.get_word_before_cursor(WORD=True)

                    # Проверяем, находимся ли мы после --columns (с пробелом или =)
                    is_after_columns = (
                            (len(words) >= 3 and words[-2] == "--columns") or  # форма: --columns <значение>
                            (len(words) >= 3 and words[
                                -1] == "--columns" and not word_before_cursor) or  # форма: --columns <пробел>
                            (word_before_cursor and word_before_cursor.startswith(
                                "--columns=")) or  # форма: --columns=<значение>
                            word_before_cursor == "--columns"  # только что написали --columns
                    )

                    if is_after_columns:
                        fragment = word_before_cursor or ""
                        # убираем префикс --columns(=)?
                        if fragment.startswith("--columns="):
                            cols_part = fragment.split("=", 1)[1]
                        elif fragment == "--columns":
                            cols_part = ""
                        elif len(words) >= 3 and words[-1] == "--columns" and not word_before_cursor:
                            # форма: --columns <пробел> (курсор после пробела)
                            cols_part = ""
                        elif len(words) >= 3 and words[-2] == "--columns":
                            # форма: --columns <значение>
                            cols_part = words[-1] if words[-1] else ""
                        else:
                            cols_part = fragment
                        for item in self._complete_columns("components", cols_part):
                            yield item
                        return

                    # Проверяем, находимся ли мы после --filter (с пробелом или =)
                    is_after_filter = (
                            (len(words) >= 3 and words[-2] == "--filter") or  # форма: --filter <значение>
                            (len(words) >= 3 and words[
                                -1] == "--filter" and not word_before_cursor) or  # форма: --filter <пробел>
                            (word_before_cursor and word_before_cursor.startswith(
                                "--filter=")) or  # форма: --filter=<значение>
                            word_before_cursor == "--filter"  # только что написали --filter
                    )

                    if is_after_filter:
                        frag = word_before_cursor or ""
                        if len(words) >= 3 and words[-1] == "--filter" and not word_before_cursor:
                            # форма: --filter <пробел> (курсор после пробела)
                            frag = ""
                        elif len(words) >= 3 and words[-2] == "--filter" and not frag.startswith("--filter"):
                            # форма: --filter <значение>
                            frag = words[-1] if words[-1] else ""
                        for item in self._complete_filter("components", frag, words):
                            yield item
                        return

                    # Иначе — подсказываем опции из Click
                    if not word_before_cursor or word_before_cursor.startswith("-"):
                        options = self._get_click_options("components", "list")
                        prefix = word_before_cursor if word_before_cursor else ""
                        for opt in options:
                            if opt.startswith(prefix):
                                yield Completion(opt, start_position=-len(prefix))
                elif len(words) >= 2 and words[1] == "upgrade":
                    # components upgrade → показываем опции и компоненты
                    word_before_cursor = document.get_word_before_cursor(WORD=True)

                    # Проверяем, есть ли уже указанные опции с параметрами
                    prev_word = words[-1] if len(words) > 2 else None
                    if prev_word in ["--from-file", "--to-tag"]:
                        # После этих опций не предлагаем ничего (пользователь должен ввести значение)
                        return

                    # Проверяем, находимся ли мы после --filter (с пробелом или =)
                    is_after_filter = (
                            (len(words) >= 3 and words[-2] == "--filter") or  # форма: --filter <значение>
                            (len(words) >= 3 and words[
                                -1] == "--filter" and not word_before_cursor) or  # форма: --filter <пробел>
                            (word_before_cursor and word_before_cursor.startswith(
                                "--filter=")) or  # форма: --filter=<значение>
                            word_before_cursor == "--filter"  # только что написали --filter
                    )

                    if is_after_filter:
                        frag = word_before_cursor or ""
                        if len(words) >= 3 and words[-1] == "--filter" and not word_before_cursor:
                            # форма: --filter <пробел> (курсор после пробела)
                            frag = ""
                        elif len(words) >= 3 and words[-2] == "--filter" and not frag.startswith("--filter"):
                            # форма: --filter <значение>
                            frag = words[-1] if words[-1] else ""
                        for item in self._complete_filter("components", frag, words):
                            yield item
                        return

                    # Если текущее слово начинается с -, показываем опции
                    if word_before_cursor and word_before_cursor.startswith("-"):
                        options = self._get_click_options("components", "upgrade")
                        prefix = word_before_cursor
                        for opt in options:
                            if opt.startswith(prefix):
                                yield Completion(opt, start_position=-len(prefix))
                        return

                    # Получаем все опции для предложения
                    options = self._get_click_options("components", "upgrade")

                    # Если нет текущего слова или оно пустое, предлагаем и опции и компоненты
                    if not word_before_cursor or len(word_before_cursor) == 0:
                        # Предлагаем опции
                        for opt in options:
                            yield Completion(opt, start_position=0)
                        # И компоненты
                        components = self.completion_manager.get_components()
                        for comp in components:
                            yield Completion(comp, start_position=0)
                        return

                    # Иначе предлагаем компоненты, но также можно предложить опции
                    components = self.completion_manager.get_components()
                    for comp in components:
                        if comp.startswith(word_before_cursor):
                            yield Completion(comp, start_position=-len(word_before_cursor))

                    # Также предлагаем опции если они начинаются с текущего слова
                    for opt in options:
                        if opt.startswith(word_before_cursor):
                            yield Completion(opt, start_position=-len(word_before_cursor))
                elif len(words) >= 2 and words[1] in ["get", "start", "stop", "tags"]:
                    # Для команд с аргументами - автодополнение имен компонентов
                    components = self.completion_manager.get_components()
                    word_before_cursor = document.get_word_before_cursor(WORD=True)
                    for comp in components:
                        if comp.startswith(word_before_cursor):
                            yield Completion(comp, start_position=-len(word_before_cursor))

            # nodes команды
            elif command == "nodes" and len(words) >= 2 and words[1] == "list":
                # nodes list → опции и умный комплишн для --columns/--filter
                word_before_cursor = document.get_word_before_cursor(WORD=True)

                # Проверяем, находимся ли мы после --columns (с пробелом или =)
                is_after_columns = (
                        (len(words) >= 3 and words[-2] == "--columns") or  # форма: --columns <значение>
                        (len(words) >= 3 and words[
                            -1] == "--columns" and not word_before_cursor) or  # форма: --columns <пробел>
                        (word_before_cursor and word_before_cursor.startswith(
                            "--columns=")) or  # форма: --columns=<значение>
                        word_before_cursor == "--columns"  # только что написали --columns
                )

                if is_after_columns:
                    fragment = word_before_cursor or ""
                    if fragment.startswith("--columns="):
                        cols_part = fragment.split("=", 1)[1]
                    elif fragment == "--columns":
                        cols_part = ""
                    elif len(words) >= 3 and words[-1] == "--columns" and not word_before_cursor:
                        # форма: --columns <пробел> (курсор после пробела)
                        cols_part = ""
                    elif len(words) >= 3 and words[-2] == "--columns":
                        # форма: --columns <значение>
                        cols_part = words[-1] if words[-1] else ""
                    else:
                        cols_part = fragment
                    for item in self._complete_columns("nodes", cols_part):
                        yield item
                    return

                # Проверяем, находимся ли мы после --filter (с пробелом или =)
                is_after_filter = (
                        (len(words) >= 3 and words[-2] == "--filter") or  # форма: --filter <значение>
                        (len(words) >= 3 and words[
                            -1] == "--filter" and not word_before_cursor) or  # форма: --filter <пробел>
                        (word_before_cursor and word_before_cursor.startswith(
                            "--filter=")) or  # форма: --filter=<значение>
                        word_before_cursor == "--filter"  # только что написали --filter
                )

                if is_after_filter:
                    frag = word_before_cursor or ""
                    if len(words) >= 3 and words[-1] == "--filter" and not word_before_cursor:
                        # форма: --filter <пробел> (курсор после пробела)
                        frag = ""
                    elif len(words) >= 3 and words[-2] == "--filter" and not frag.startswith("--filter"):
                        # форма: --filter <значение>
                        frag = words[-1] if words[-1] else ""
                    for item in self._complete_filter("nodes", frag, words):
                        yield item
                    return

                # Иначе — подсказываем опции из Click
                if not word_before_cursor or word_before_cursor.startswith("-"):
                    options = self._get_click_options("nodes", "list")
                    prefix = word_before_cursor if word_before_cursor else ""
                    for opt in options:
                        if opt.startswith(prefix):
                            yield Completion(opt, start_position=-len(prefix))
            elif command == "nodes" and len(words) >= 2 and words[1] in ["get", "update"]:
                # nodes get/update → показываем имена нод
                nodes = self.completion_manager.get_nodes()
                word_before_cursor = document.get_word_before_cursor(WORD=True)
                for node in nodes:
                    if node.startswith(word_before_cursor):
                        yield Completion(node, start_position=-len(word_before_cursor))

            # stacks команды
            elif command == "stacks" and len(words) >= 2 and words[1] == "list":
                # stacks list → опции и умный комплишн для --columns/--filter
                word_before_cursor = document.get_word_before_cursor(WORD=True)
                # Проверяем, находимся ли мы после --columns (с пробелом или =)
                is_after_columns = (
                        (len(words) >= 3 and words[-2] == "--columns") or  # форма: --columns <значение>
                        (len(words) >= 3 and words[
                            -1] == "--columns" and not word_before_cursor) or  # форма: --columns <пробел>
                        (word_before_cursor and word_before_cursor.startswith(
                            "--columns=")) or  # форма: --columns=<значение>
                        word_before_cursor == "--columns"  # только что написали --columns
                )

                if is_after_columns:
                    fragment = word_before_cursor or ""
                    if fragment.startswith("--columns="):
                        cols_part = fragment.split("=", 1)[1]
                    elif fragment == "--columns":
                        cols_part = ""
                    elif len(words) >= 3 and words[-1] == "--columns" and not word_before_cursor:
                        # форма: --columns <пробел> (курсор после пробела)
                        cols_part = ""
                    elif len(words) >= 3 and words[-2] == "--columns":
                        # форма: --columns <значение>
                        cols_part = words[-1] if words[-1] else ""
                    else:
                        cols_part = fragment
                    for item in self._complete_columns("stacks", cols_part):
                        yield item
                    return

                # Проверяем, находимся ли мы после --filter (с пробелом или =)
                is_after_filter = (
                        (len(words) >= 3 and words[-2] == "--filter") or  # форма: --filter <значение>
                        (len(words) >= 3 and words[
                            -1] == "--filter" and not word_before_cursor) or  # форма: --filter <пробел>
                        (word_before_cursor and word_before_cursor.startswith(
                            "--filter=")) or  # форма: --filter=<значение>
                        word_before_cursor == "--filter"  # только что написали --filter
                )

                if is_after_filter:
                    frag = word_before_cursor or ""
                    if len(words) >= 3 and words[-1] == "--filter" and not word_before_cursor:
                        # форма: --filter <пробел> (курсор после пробела)
                        frag = ""
                    elif len(words) >= 3 and words[-2] == "--filter" and not frag.startswith("--filter"):
                        # форма: --filter <значение>
                        frag = words[-1] if words[-1] else ""
                    for item in self._complete_filter("stacks", frag, words):
                        yield item
                    return

                if not word_before_cursor or word_before_cursor.startswith("-"):
                    options = self._get_click_options("stacks", "list")
                    prefix = word_before_cursor if word_before_cursor else ""
                    for opt in options:
                        if opt.startswith(prefix):
                            yield Completion(opt, start_position=-len(prefix))
            elif command == "stacks" and len(words) >= 2 and words[1] in ["get", "undeploy"]:
                # stacks get/undeploy → показываем имена стеков
                stacks = self.completion_manager.get_stacks()
                word_before_cursor = document.get_word_before_cursor(WORD=True)
                for stack in stacks:
                    if stack.startswith(word_before_cursor):
                        yield Completion(stack, start_position=-len(word_before_cursor))

            # logs команды
            elif command == "logs":
                word_before_cursor = document.get_word_before_cursor(WORD=True)

                # Проверяем, находимся ли мы после опции, которая требует значения
                if len(words) > 1:
                    prev_word = words[-2]  # Предыдущее слово (опция)
                    if prev_word in ["--lines", "-n", "--tail", "-t"]:
                        # После этих опций не предлагаем ничего (пользователь должен ввести значение)
                        return

                # Если текущее слово начинается с -, показываем опции
                if word_before_cursor and word_before_cursor.startswith("-"):
                    options = self._get_click_options("logs", "")
                    prefix = word_before_cursor
                    for opt in options:
                        if opt.startswith(prefix):
                            yield Completion(opt, start_position=-len(prefix))
                    return

                # Определяем позицию аргумента компонента
                # Для команды logs аргумент обязателен, он идет сразу после команды
                # Если len(words) == 1, значит только "logs" или "logs " - это позиция аргумента
                # Если len(words) == 1 и ends_with_space, точно позиция аргумента (курсор после пробела)
                # Если len(words) == 1 и есть word_before_cursor не начинающийся с "-", тоже позиция аргумента
                is_component_arg_position = (
                        len(words) == 1  # "logs" или "logs " - всегда позиция аргумента компонента
                )

                # Если это позиция аргумента компонента
                if is_component_arg_position:
                    components = self.completion_manager.get_components()
                    prefix = word_before_cursor or ""

                    # Предлагаем компоненты
                    for comp in components:
                        if not prefix or comp.startswith(prefix):
                            start_pos = -len(prefix) if prefix else 0
                            yield Completion(comp, start_position=start_pos)

                    # Также предлагаем опции, если курсор в начале слова (после пробела)
                    if not prefix or len(prefix) == 0 or ends_with_space:
                        options = self._get_click_options("logs", "")
                        for opt in options:
                            yield Completion(opt, start_position=0)
                else:
                    # Если уже есть компонент или опции, показываем только опции
                    if word_before_cursor:
                        if word_before_cursor.startswith("-"):
                            options = self._get_click_options("logs", "")
                            prefix = word_before_cursor
                            for opt in options:
                                if opt.startswith(prefix):
                                    yield Completion(opt, start_position=-len(prefix))
                        else:
                            # Если начинаем вводить что-то еще, предлагаем компоненты и опции
                            components = self.completion_manager.get_components()
                            for comp in components:
                                if comp.startswith(word_before_cursor):
                                    yield Completion(comp, start_position=-len(word_before_cursor))
                            options = self._get_click_options("logs", "")
                            for opt in options:
                                if opt.startswith(word_before_cursor):
                                    yield Completion(opt, start_position=-len(word_before_cursor))
                    else:
                        # Пустое слово - показываем опции
                        options = self._get_click_options("logs", "")
                        for opt in options:
                            yield Completion(opt, start_position=0)

            # Обработка команды shell с автодополнением имени сервера
            if command == "shell":
                # Автодополнение для аргумента server в команде shell
                word_before_cursor = document.get_word_before_cursor(WORD=True)
                servers = self.completion_manager.get_servers()
                for server in servers:
                    if server.lower().startswith(word_before_cursor.lower()):
                        yield Completion(server, start_position=-len(word_before_cursor))
                return

            # Используем статический completer как fallback
            for item in self.static_completer.get_completions(document, complete_event):
                yield item

    return ImgctlCompleter(completion_manager, commands_dict)


def create_prompt_session(ctx, completion_manager: CompletionManager):
    """Создает сессию REPL с автодополнением и историей"""
    if not PROMPT_TOOLKIT_AVAILABLE:
        console.print("[red]prompt-toolkit не установлен. Установите: pip install prompt-toolkit[/red]")
        return None

    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.key_binding import KeyBindings

    # Создаем историю в домашней директории
    history_file = Path.home() / ".imgctl_history"
    history = FileHistory(str(history_file))

    # Создаем completer используя контекст
    from cli.main import main
    ctx_copy = click.Context(main)
    completer = create_imgctl_completer(ctx_copy, completion_manager)

    # Key bindings для удобства
    kb = KeyBindings()

    @kb.add("c-c")
    def _(event):
        """Ctrl+C для выхода"""
        event.app.exit()

    # Получаем цвета из конфига для промпта
    try:
        api = _get_api_client_from_ctx(ctx, verbose=False)
        if api:
            console_config = api.get_console_config()
            console_name = console_config.get("consoleName", "imgctl")
            console_color = console_config.get("consoleColor", "#00D9FF")
        else:
            console_name = "imgctl"
            console_color = "#00D9FF"
    except Exception:
        console_name = "imgctl"
        console_color = "#00D9FF"

    # Создаем промпт с цветом фона в стиле zsh
    # hex цвет конвертируем в RGB для правильного отображения
    hex_color = console_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    # Определяем цвет фона и текста на основе яркости
    r, g, b = rgb
    # Вычисляем яркость для определения цвета текста
    brightness = (r * 299 + g * 587 + b * 114) / 1000

    def create_prompt():
        """Динамически создает промпт с именем стенда через Rich"""
        # Формат: "imgctl (имя стенда)> "
        from rich.text import Text
        from rich.console import Console

        # Создаем цветной текст с заливкой через Rich
        prompt_text = Text(f"{console_name}> ", style=f"bold white on {console_color}")

        # Конвертируем в ANSI через Rich
        console_temp = Console(force_terminal=False, legacy_windows=False, color_system="auto")
        with console_temp.capture() as capture:
            console_temp.print(prompt_text, end="")
        ansi_str = capture.get()

        # Rich генерирует правильные ANSI коды
        return ansi_str

    # Создаем сессию с автодополнением, но без выпадающего меню
    session = PromptSession(
        history=history,
        completer=completer,
        auto_suggest=AutoSuggestFromHistory(),
        key_bindings=kb,
        message=create_prompt,
        refresh_interval=0.1,
        rprompt='',
        complete_while_typing=False,  # Автодополнение только по Tab
        complete_style='readline',  # Стиль Readline без выпадающего списка
        enable_open_in_editor=True,
        enable_suspend=True,
    )

    return session


def process_command(ctx, command_text: str) -> bool:
    """
    Обрабатывает команду в REPL режиме

    Returns:
        bool: True если нужно выйти из REPL
    """
    # Проверяем что текст не None и не пустой
    if not command_text:
        return False

    command_text = command_text.strip()
    if not command_text:
        return False

    # Специальные команды REPL
    if command_text.lower() in ["exit", "quit"]:
        return True
    elif command_text.lower() == "help":
        show_repl_help(ctx)
        return False
    elif command_text.lower() == "clear":
        click.clear()
        return False

    # Парсим команду через shlex для правильной обработки кавычек
    try:
        parts = shlex.split(command_text)
        if not parts:
            return False

        # Вызываем Click команду через context
        return invoke_command(ctx, parts)

    except Exception as e:
        console.print(f"[red]Ошибка выполнения команды: {e}[/red]")
        import traceback

        traceback.print_exc()
        return False


def _show_header_from_api_client(api_client):
    """Показывает заголовок консоли на основе API клиента"""
    try:
        from utils.formatters import display_console_header
        
        config = api_client.get_console_config()
        console_name = config.get("consoleName", "Imagenarium")
        console_color = config.get("consoleColor", "#ffffff")
        try:
            version = api_client.get_version()
        except Exception:
            version = None
        display_console_header(console_name, console_color, version)
        return True
    except Exception:
        return False


def _show_parent_shell_header(parent_api_client, ctx):
    """Показывает заголовок родительского shell после выхода из вложенного"""
    try:
        from utils.formatters import display_console_header
        
        # Пробуем использовать сохраненный API клиент
        if parent_api_client and _show_header_from_api_client(parent_api_client):
            return
        
        # Пробуем создать API клиент из контекста
        if ctx and hasattr(ctx, 'obj'):
            api = _get_api_client_from_ctx(ctx, verbose=False)
            if api and _show_header_from_api_client(api):
                return
        
        # Fallback: заголовок по умолчанию
        display_console_header("Imagenarium", "#ffffff")
    except Exception:
        pass


def invoke_command(ctx, parts: List[str]) -> bool:
    """
    Вызывает Click команду из REPL

    Args:
        ctx: Click контекст
        parts: Разобранные части команды

    Returns:
        bool: True если нужно выйти
    """
    # Сохраняем оригинальный sys.argv
    old_argv = sys.argv[:]
    
    # Проверяем, была ли вызвана команда shell (вложенный shell)
    is_nested_shell = len(parts) > 0 and parts[0] == "shell"
    
    # Сохраняем контекст родительского shell для показа заголовка после выхода
    parent_api_client = None
    if is_nested_shell and ctx and hasattr(ctx, 'obj'):
        # Пробуем получить API клиент из контекста
        parent_api_client = ctx.obj.get('api')
        # Если API клиента нет в контексте, создаем его динамически
        if not parent_api_client:
            parent_api_client = _get_api_client_from_ctx(ctx, verbose=False)

    try:
        # Устанавливаем новый argv
        # Устанавливаем флаг shell-mode в переменной окружения
        # чтобы команды знали что нужно использовать кэш и не показывать заголовок
        os.environ["IMGCTL_SHELL_MODE"] = "1"

        # Добавляем параметры командной строки из ctx.obj если они есть
        argv_parts = ["imgctl"]

        # Добавляем параметры из ctx.obj если они установлены при запуске shell
        if ctx and hasattr(ctx, 'obj'):
            server = ctx.obj.get('server')
            if server:
                argv_parts.extend(['--server', server])
            username = ctx.obj.get('username')
            password = ctx.obj.get('password')
            if username and password:
                argv_parts.extend(['--username', username, '--password', password])

        # Добавляем части команды пользователя
        argv_parts.extend(parts)

        sys.argv = argv_parts

        # Получаем главную функцию
        from cli.main import main

        # Вызываем main напрямую
        # Click сам разберет аргументы из sys.argv
        main()

        # Если это была команда shell и мы вернулись (не было SystemExit),
        # показываем заголовок родительского shell
        if is_nested_shell:
            # Показываем заголовок родительского shell
            _show_parent_shell_header(parent_api_client, ctx)

        return False

    except SystemExit as e:
        # Click может вызывать SystemExit для выхода
        # Если это был вложенный shell, показываем заголовок родительского
        if is_nested_shell:
            _show_parent_shell_header(parent_api_client, ctx)
        # Не пробрасываем SystemExit дальше, иначе родительский shell может закрыться
        if e.code != 0:
            raise
    except KeyboardInterrupt:
        console.print("\n[yellow]Прервано пользователем[/yellow]")
    except Exception as e:
        console.print(f"[red]Ошибка: {e}[/red]")
        import traceback

        traceback.print_exc()
    finally:
        sys.argv = old_argv
        # Убираем флаг только если это не была команда shell
        # (для shell флаг уже восстановлен выше)
        if not is_nested_shell:
            os.environ.pop("IMGCTL_SHELL_MODE", None)

    return False


def show_repl_help(ctx):
    """Показывает справку по REPL используя Click"""
    from cli.main import main

    help_text = """## imgctl REPL - Интерактивная оболочка

### Доступные команды:

"""

    # Получаем список команд из Click
    commands_list = []
    for cmd_name, cmd in main.commands.items():
        cmd_help = cmd.get_short_help_str() if hasattr(cmd, 'get_short_help_str') else ""
        commands_list.append(f"**{cmd_name}** - {cmd_help}")

    help_text += "\n".join(commands_list)
    help_text += """

### Специальные команды:
- `help` - Показать эту справку
- `clear` - Очистить экран  
- `exit` или `quit` - Выйти из REPL

### Примеры:
```bash
imgctl> components list
imgctl> components get web-api-staging
imgctl> servers list
imgctl> exit
```

### Советы:
- Используйте TAB для автодополнения
- Используйте стрелки для истории команд
- Введите `команда --help` для справки по команде
"""

    console.print(Markdown(help_text))


def background_cache_updater(ctx):
    """
    Фоновый поток для обновления кэша компонентов каждые 5 секунд
    Использует API клиент из контекста с async_mode=True для бесшумного обновления
    """
    while not _stop_cache_updates.wait(timeout=5):
        try:
            # Помечаем что загрузка началась
            with _cache_update_lock:
                _cache_update_in_progress.set()

            # Используем API клиент из контекста (уже с async_mode=True)
            # Не нужно убирать IMGCTL_SHELL_MODE - используем существующий API клиент
            invoke_cache_update(ctx, no_cache=True)

            # Помечаем что загрузка завершена
            with _cache_update_lock:
                _cache_update_in_progress.clear()
        except Exception:
            # Игнорируем ошибки в фоновом потоке
            with _cache_update_lock:
                _cache_update_in_progress.clear()
            pass


def invoke_cache_update(ctx, no_cache=True):
    """
    Выполняет обновление кэша компонентов в фоне через API клиент

    Args:
        ctx: Click контекст
        no_cache: Если True, игнорирует кэш при чтении и загружает свежие данные
    """
    try:
        # Получаем API клиент из контекста (должен быть уже с async_mode=True)
        # Не используем verbose в фоновом потоке для тишины
        api = _get_api_client_from_ctx(ctx, verbose=False)

        if api:
            # Вызываем API метод
            # no_cache=True для фонового потока (всегда обновляем, игнорируя кеш при чтении)
            api.get_components(no_cache=no_cache)
    except Exception:
        # Игнорируем ошибки в фоновом потоке
        pass


def start_background_cache_updater(ctx):
    """
    Запускает фоновый поток для обновления кэша
    """
    global _cache_update_thread
    global _stop_cache_updates

    if _cache_update_thread is None or not _cache_update_thread.is_alive():
        _stop_cache_updates.clear()
        _cache_update_thread = threading.Thread(
            target=background_cache_updater,
            args=(ctx,),
            daemon=True,
            name="imgctl_cache_updater"
        )
        _cache_update_thread.start()


def stop_background_cache_updater():
    """
    Останавливает фоновый поток для обновления кэша
    """
    global _stop_cache_updates
    _stop_cache_updates.set()


def show_welcome(ctx):
    """Показывает стандартный заголовок консоли"""
    try:
        from utils.formatters import show_console_header

        # Получаем API клиент из контекста или создаем новый
        verbose = ctx.obj.get('verbose', False) if ctx and hasattr(ctx, 'obj') else False
        api = _get_api_client_from_ctx(ctx, verbose=verbose)

        if api:
            show_console_header(api, show_header=True)
        else:
            # Fallback: заголовок по умолчанию
            from utils.formatters import display_console_header
            display_console_header("Imagenarium")
    except Exception:
        # Fallback: заголовок по умолчанию
        try:
            from utils.formatters import display_console_header
            display_console_header("Imagenarium")
        except Exception:
            pass


@click.command("shell")
@click.argument("server", required=False)
@click.pass_context
def shell(ctx, server):
    """
    Запускает интерактивную оболочку imgctl (REPL режим)

    Позволяет выполнять команды imgctl в интерактивном режиме
    с поддержкой автодополнения и истории команд.

    Пример использования:

    \b
        $ imgctl shell
        imgctl> components list
        imgctl> components get web-api-staging
        imgctl> exit

        $ imgctl shell dev
        $ imgctl shell stage
    """
    # Определяем сервер: сначала из аргумента команды, затем из ctx.obj (--server опция)
    if ctx.obj is None:
        ctx.obj = {}

    # Если сервер указан как позиционный аргумент, используем его
    # Иначе проверяем, был ли передан --server в главной команде
    final_server = server or ctx.obj.get('server')
    if final_server:
        ctx.obj['server'] = final_server

    if not PROMPT_TOOLKIT_AVAILABLE:
        console.print("[red]Ошибка: prompt-toolkit не установлен[/red]")
        console.print("[yellow]Установите: pip install prompt-toolkit[/yellow]")
        return

    # Устанавливаем флаг shell-mode ДО создания API клиента
    # чтобы API клиент создавался с async_mode=True
    # Временно убираем для показа заголовка, но затем восстановим
    temp_shell_mode = os.environ.pop("IMGCTL_SHELL_MODE", None)
    
    # Показываем стандартный заголовок (без IMGCTL_SHELL_MODE)
    show_welcome(ctx)
    
    # Устанавливаем флаг shell-mode для команд внутри shell и API клиента
    os.environ["IMGCTL_SHELL_MODE"] = "1"
    
    # Инициализируем CompletionManager для автодополнения
    # Передаем указанный сервер или None для использования текущего сервера
    # Используем API клиент из контекста для переиспользования кэша
    api_client_from_ctx = ctx.obj.get('api') if ctx.obj else None
    # Если API клиента нет в контексте или он создан без async_mode, создаем новый
    if not api_client_from_ctx:
        api_client_from_ctx = _get_api_client_from_ctx(ctx, verbose=False)
        if api_client_from_ctx and ctx.obj:
            ctx.obj['api'] = api_client_from_ctx
    # Если API клиент есть, но он был создан без async_mode, пересоздаем его
    elif api_client_from_ctx and not api_client_from_ctx.async_mode:
        api_client_from_ctx = _get_api_client_from_ctx(ctx, verbose=False)
        if api_client_from_ctx and ctx.obj:
            ctx.obj['api'] = api_client_from_ctx
    
    completion_manager = CompletionManager(
        server_name=final_server,
        api_client=api_client_from_ctx
    )

    # Запускаем фоновое обновление кэша
    start_background_cache_updater(ctx)

    # НЕ предзагружаем данные сразу - пусть фоновое обновление делает это
    # Автодополнение будет использовать данные из кэша когда они появятся

    # Создаем сессию
    session = create_prompt_session(ctx, completion_manager)
    if session is None:
        return

    # Основной цикл REPL
    while True:
        try:
            # Получаем команду от пользователя (промпт берется из message функции)
            text = session.prompt()

            # Обрабатываем команду только если текст не пустой
            if text:
                should_exit = process_command(ctx, text)

                if should_exit:
                    break
            else:
                # Если text is None (EOF), выходим
                break

        except KeyboardInterrupt:
            # Ctrl+C - показываем сообщение
            console.print("\n[yellow]Нажмите Ctrl+C еще раз для выхода или введите exit[/yellow]")
            try:
                text = session.prompt()
                should_exit = process_command(ctx, text)
                if should_exit:
                    break
            except (KeyboardInterrupt, EOFError):
                break
        except EOFError:
            # Ctrl+D - выход
            break

    # Останавливаем фоновое обновление кэша
    stop_background_cache_updater()
