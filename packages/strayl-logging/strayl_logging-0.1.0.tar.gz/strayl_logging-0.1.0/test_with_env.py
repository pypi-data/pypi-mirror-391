"""
Пример использования SDK с переменными окружения.

Это более безопасный способ - ключ не хранится в коде.

Установка:
1. pip install python-dotenv  # для загрузки .env файла
2. Создайте .env файл с вашим ключом (см. .env.example)
3. Запустите: python test_with_env.py
"""

import os
from strayl_logging import StraylLogger

# Попытка загрузить из .env (если установлен python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("💡 Совет: установите python-dotenv для загрузки .env файла")
    print("   pip install python-dotenv")

def main():
    """Тестирование с ключом из переменной окружения."""
    
    # Получаем ключ из переменной окружения
    api_key = os.getenv("STRAYL_API_KEY")
    
    if not api_key:
        print("❌ Ошибка: STRAYL_API_KEY не найден!")
        print("\n📝 Как исправить:")
        print("   1. Создайте файл .env в этой папке")
        print("   2. Добавьте строку: STRAYL_API_KEY=st_ваш_ключ")
        print("   3. Или установите переменную окружения:")
        print("      export STRAYL_API_KEY=st_ваш_ключ  # Linux/Mac")
        print("      set STRAYL_API_KEY=st_ваш_ключ      # Windows")
        return
    
    if api_key == "st_ваш_ключ_здесь" or api_key.startswith("st_ТВОЙ"):
        print("❌ Ошибка: Замените 'st_ваш_ключ_здесь' на ваш реальный ключ!")
        print("   Получите ключ на https://strayl.dev/dashboard → вкладка API")
        return
    
    # Инициализация логгера
    logger = StraylLogger(
        api_key=api_key,
        default_context={"service": "python-test", "env": "local"},
    )
    
    print("✅ API ключ загружен из переменной окружения")
    print("📤 Отправка тестовых логов...\n")
    
    # Тест info
    logger.info("Test log from Python SDK (env)", {"test_type": "info"})
    
    # Тест warn
    logger.warn("Test warning log (env)", {"test_type": "warn"})
    
    # Тест error
    logger.error("Test error log (env)", {"test_type": "error"})
    
    # Тест debug
    logger.debug("Test debug log (env)", {"test_type": "debug"})
    
    print("\n✅ Логи отправлены! Проверьте их в Dashboard:")
    print("   https://strayl.dev/dashboard → вкладка Logs")


if __name__ == "__main__":
    main()

