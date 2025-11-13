"""
Клиент для отправки логов в Strayl Cortyx.

Этот модуль предоставляет класс StraylLogger для отправки логов
через API ключи в централизованное хранилище Strayl.
"""

import threading
from typing import Any, Dict, Optional


try:
    import requests
except ImportError:
    raise ImportError(
        "strayl-logging requires 'requests' package. "
        "Install it with: pip install requests"
    )


class StraylLogger:
    """
    Минималистичный Python логгер для Strayl Cortyx.

    Отправляет логи через API ключи в централизованное хранилище.
    Логи не должны ломать приложение пользователя, поэтому все ошибки
    отправки логируются молча.

    Пример использования:
        >>> from strayl_logging import StraylLogger
        >>> logger = StraylLogger(api_key="st_...")
        >>> logger.info("Server started", {"port": 8000})
        >>> logger.error("Connection failed", {"retry": True})

    Attributes:
        api_key: API ключ для аутентификации (формат st_...)
        endpoint: URL эндпоинта для отправки логов
        default_context: Контекст по умолчанию для всех логов
        timeout: Таймаут запроса в секундах
        async_mode: Если True, отправка выполняется в отдельном потоке
    """

    # URL эндпоинта по умолчанию
    DEFAULT_ENDPOINT = "https://ougtygyvcgdnytkswier.supabase.co/functions/v1/log"

    # Поддерживаемые уровни логов
    VALID_LEVELS = {"info", "warn", "error", "debug"}

    def __init__(
        self,
        api_key: str,
        endpoint: Optional[str] = None,
        default_context: Optional[Dict[str, Any]] = None,
        timeout: float = 3.0,
        async_mode: bool = True,
    ) -> None:
        """
        Инициализация StraylLogger.

        Args:
            api_key: API ключ для аутентификации (обязательный)
            endpoint: URL эндпоинта (по умолчанию используется DEFAULT_ENDPOINT)
            default_context: Контекст по умолчанию для всех логов
            timeout: Таймаут запроса в секундах (по умолчанию 3.0)
            async_mode: Если True, отправка выполняется асинхронно в отдельном потоке

        Raises:
            ValueError: Если api_key не указан или пустой
        """
        if not api_key:
            raise ValueError("StraylLogger: api_key is required")

        if not api_key.startswith("st_"):
            raise ValueError(
                "StraylLogger: api_key must start with 'st_' prefix. "
                "Get your API key from https://strayl.dev/dashboard"
            )

        self.api_key = api_key
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT
        self.default_context = default_context or {}
        self.timeout = timeout
        self.async_mode = async_mode

    def _send(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Внутренний метод для отправки лога на сервер.

        Args:
            level: Уровень лога (info, warn, error, debug)
            message: Текст сообщения
            context: Дополнительный контекст для лога

        Note:
            Все ошибки отправки проглатываются, чтобы не ломать приложение.
        """
        # Валидация уровня
        if level not in self.VALID_LEVELS:
            level = "info"  # Fallback на info при неверном уровне

        # Формирование payload
        payload = {
            "level": level,
            "message": message,
            "context": {**self.default_context, **(context or {})},
        }

        try:
            response = requests.post(
                self.endpoint,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,  # requests автоматически сериализует в JSON
                timeout=self.timeout,
            )

            # Проверка статуса ответа (не бросаем исключение, только логируем)
            if response.status_code not in (200, 201):
                # В production можно добавить логирование через logging.debug
                pass

        except requests.exceptions.Timeout:
            # Таймаут - не критично для логгера
            pass
        except requests.exceptions.RequestException:
            # Любые другие ошибки сети - проглатываем
            pass
        except Exception:
            # Любые неожиданные ошибки - проглатываем
            # Логгер не должен ломать приложение пользователя
            pass

    def log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Отправка лога с указанным уровнем.

        Args:
            level: Уровень лога (info, warn, error, debug)
            message: Текст сообщения
            context: Дополнительный контекст (объединяется с default_context)

        Example:
            >>> logger.log("info", "User logged in", {"user_id": 123})
        """
        if self.async_mode:
            # Асинхронная отправка в отдельном потоке
            thread = threading.Thread(
                target=self._send,
                args=(level, message, context),
                daemon=True,  # Поток не блокирует завершение программы
            )
            thread.start()
        else:
            # Синхронная отправка
            self._send(level, message, context)

    def info(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Отправка информационного лога.

        Args:
            message: Текст сообщения
            context: Дополнительный контекст

        Example:
            >>> logger.info("Server started", {"port": 8000})
        """
        self.log("info", message, context)

    def warn(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Отправка предупреждения.

        Args:
            message: Текст сообщения
            context: Дополнительный контекст

        Example:
            >>> logger.warn("High memory usage", {"usage": "85%"})
        """
        self.log("warn", message, context)

    def error(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Отправка ошибки.

        Args:
            message: Текст сообщения
            context: Дополнительный контекст

        Example:
            >>> logger.error("Database connection failed", {"retry": True})
        """
        self.log("error", message, context)

    def debug(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Отправка отладочного лога.

        Args:
            message: Текст сообщения
            context: Дополнительный контекст

        Example:
            >>> logger.debug("Processing request", {"request_id": "abc123"})
        """
        self.log("debug", message, context)

