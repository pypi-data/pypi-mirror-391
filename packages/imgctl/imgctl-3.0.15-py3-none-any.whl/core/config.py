"""
Конфигурация для imgctl

Модуль для управления конфигурацией приложения.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any


class Config:
    """Класс для управления конфигурацией imgctl"""

    def __init__(self):
        self.server: str = "http://localhost:5555"
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.timeout: int = 30
        self.verify_ssl: bool = True

    def load_from_file(self, config_path: Optional[str] = None) -> None:
        """Загружает конфигурацию из файла"""
        if config_path is None:
            if os.name == "nt":  # Windows
                # Windows: %APPDATA%/imgctl/config.yaml
                config_path = os.path.join(
                    os.environ.get("APPDATA", ""), "imgctl", "config.yaml"
                )
            else:  # Unix-like (Linux, macOS)
                # Unix: ~/.config/imgctl/config.yaml
                config_path = os.path.expanduser("~/.config/imgctl/config.yaml")

        config_file = Path(config_path)
        if not config_file.exists():
            return

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data:
                self.server = data.get("server", self.server)
                self.username = data.get("username", self.username)
                self.password = data.get("password", self.password)
                self.timeout = data.get("timeout", self.timeout)
                self.verify_ssl = data.get("verify_ssl", self.verify_ssl)

        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")

    def load_from_env(self) -> None:
        """Загружает конфигурацию из переменных окружения"""
        self.server = os.getenv("IMGCTL_SERVER", self.server)
        self.username = os.getenv("IMGCTL_USERNAME", self.username)
        self.password = os.getenv("IMGCTL_PASSWORD", self.password)

        timeout_str = os.getenv("IMGCTL_TIMEOUT")
        if timeout_str:
            try:
                self.timeout = int(timeout_str)
            except ValueError:
                pass

        verify_ssl_str = os.getenv("IMGCTL_VERIFY_SSL", "true").lower()
        self.verify_ssl = verify_ssl_str in ("true", "1", "yes", "on")

    def to_dict(self) -> Dict[str, Any]:
        """Возвращает конфигурацию в виде словаря"""
        return {
            "server": self.server,
            "username": self.username,
            "password": self.password,
            "timeout": self.timeout,
            "verify_ssl": self.verify_ssl,
        }
