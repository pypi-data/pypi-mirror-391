"""
Модуль для обеспечения безопасности данных
"""

import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pathlib import Path
from typing import Optional


class SecurityManager:
    """Менеджер безопасности для шифрования чувствительных данных"""

    def __init__(self):
        self._key: Optional[bytes] = None
        self._fernet: Optional[Fernet] = None

    def _get_or_create_key(self) -> bytes:
        """Получает или создает ключ шифрования"""
        if self._key is not None:
            return self._key

        # Генерируем ключ на основе уникальных данных пользователя
        key_source = self._get_key_source()

        # Используем PBKDF2 для генерации ключа
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"imgctl_salt_2024",  # Фиксированная соль для консистентности
            iterations=100000,
        )

        self._key = base64.urlsafe_b64encode(kdf.derive(key_source.encode()))
        self._fernet = Fernet(self._key)

        return self._key

    def _get_key_source(self) -> str:
        """Получает уникальные данные пользователя для генерации ключа"""
        import getpass

        # Комбинируем несколько источников для уникальности
        sources = []

        # Имя пользователя
        try:
            sources.append(getpass.getuser())
        except:
            sources.append("default_user")

        # Домашняя директория
        try:
            sources.append(str(Path.home()))
        except:
            sources.append("/tmp")

        # Идентификатор машины (если доступен)
        try:
            if os.name == "nt":  # Windows
                import winreg

                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
                )
                machine_guid = winreg.QueryValueEx(key, "MachineGuid")[0]
                sources.append(machine_guid)
            else:  # Unix-like
                # Используем machine-id если доступен
                machine_id_file = Path("/etc/machine-id")
                if machine_id_file.exists():
                    sources.append(machine_id_file.read_text().strip())
                else:
                    # Fallback на hostname
                    import socket

                    sources.append(socket.gethostname())
        except:
            sources.append("fallback_machine_id")

        return "|".join(sources)

    def encrypt(self, data: str) -> str:
        """Шифрует строку"""
        if not data:
            return data

        try:
            key = self._get_or_create_key()
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception:
            # Если шифрование не удалось, возвращаем исходные данные
            # В продакшене здесь должен быть лог ошибки
            return data

    def decrypt(self, encrypted_data: str) -> str:
        """Расшифровывает строку"""
        if not encrypted_data:
            return encrypted_data

        try:
            key = self._get_or_create_key()
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception:
            # Если расшифровка не удалась, возвращаем исходные данные
            # Возможно, данные не зашифрованы (обратная совместимость)
            return encrypted_data

    def hash_password(self, password: str) -> str:
        """Создает хеш пароля для безопасного хранения"""
        if not password:
            return password

        # Используем PBKDF2 с солью
        salt = os.urandom(32)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )

        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(salt + key).decode()

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Проверяет пароль против хеша"""
        if not password or not hashed_password:
            return False

        try:
            # Извлекаем соль и ключ из хеша
            decoded = base64.urlsafe_b64decode(hashed_password.encode())
            salt = decoded[:32]
            stored_key = decoded[32:]

            # Вычисляем ключ для данного пароля
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )

            computed_key = kdf.derive(password.encode())

            # Сравниваем ключи
            return computed_key == stored_key
        except Exception:
            return False


# Глобальный экземпляр менеджера безопасности
_security_manager = SecurityManager()


def encrypt_sensitive_data(data: str) -> str:
    """Шифрует чувствительные данные"""
    return _security_manager.encrypt(data)


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Расшифровывает чувствительные данные"""
    return _security_manager.decrypt(encrypted_data)


def hash_password(password: str) -> str:
    """Создает хеш пароля"""
    return _security_manager.hash_password(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Проверяет пароль"""
    return _security_manager.verify_password(password, hashed_password)
