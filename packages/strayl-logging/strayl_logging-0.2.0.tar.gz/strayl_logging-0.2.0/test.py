"""
Локальный тест для проверки работы StraylLogger.

Перед запуском:
1. Установите пакет локально: pip install -e .
2. Замените 'st_ТВОЙ_КЛЮЧ' на ваш реальный API ключ (строка 19)
3. Запустите: python test.py

ВАЖНО: Получите ключ на https://strayl.dev/dashboard → вкладка API
"""

from strayl_logging import StraylLogger
import os


def main():
    """Тестирование всех методов StraylLogger."""
    # ============================================
    # 👇 ВСТАВЬТЕ ВАШ API КЛЮЧ СЮДА 👇
    # ============================================
    # Вариант 1: Прямо в коде (для теста)
    API_KEY = "st_d47bea6db0dc447681121b43c0bf0f8718b53010"  # <-- ЗАМЕНИТЕ ЭТО на ваш ключ!
    
    # Вариант 2: Из переменной окружения (рекомендуется)
    # API_KEY = os.getenv("STRAYL_API_KEY", "st_ТВОЙ_КЛЮЧ")
    # ============================================
    
    # Инициализация логгера
    logger = StraylLogger(
        api_key=API_KEY,  # Используем ключ здесь
        default_context={"service": "python-test", "env": "local"},
    )

    print("Отправка тестовых логов...")
    print(f"📡 Endpoint: {logger.endpoint}")
    print(f"🔑 API Key: {API_KEY[:20]}...")
    print()

    # Тест info
    logger.info("Test log from Python SDK", {"test_type": "info"})

    # Тест warn
    logger.warn("Test warning log", {"test_type": "warn"})

    # Тест error
    logger.error("Test error log", {"test_type": "error"})

    # Тест debug
    logger.debug("Test debug log", {"test_type": "debug"})

    # Тест с кастомным контекстом
    logger.info(
        "Test log with custom context",
        {"custom_field": "custom_value", "number": 42},
    )

    print("Логи отправлены! Проверьте их в Dashboard: https://strayl.dev/dashboard")


if __name__ == "__main__":
    main()

