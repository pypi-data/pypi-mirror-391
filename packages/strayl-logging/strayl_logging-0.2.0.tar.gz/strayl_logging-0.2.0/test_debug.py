"""
Тест с отладкой - показывает все ошибки и ответы сервера.

Используйте этот файл, чтобы понять, почему логи не появляются.

Перед запуском:
1. Установите пакет: pip install -e .
2. Или запустите из корня проекта
"""

import sys
import os
import requests
import json

# Добавляем путь к модулю для импорта без установки
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from strayl_logging import StraylLogger
except ImportError:
    print("⚠️ Не удалось импортировать StraylLogger")
    print("💡 Установите пакет: pip install -e .")
    print("   Или запустите тест из корня проекта")
    sys.exit(1)

# Ваш API ключ
API_KEY = "st_d47bea6db0dc447681121b43c0bf0f8718b53010"

# ⚠️ ВАЖНО: Если получаете 401, значит Edge Function не проверяет API ключи
# Нужно задеплоить правильную версию функции (см. EDGE_FUNCTION_FIX.md)

# Endpoint
ENDPOINT = "https://ougtygyvcgdnytkswier.supabase.co/functions/v1/log"

print("=" * 60)
print("🔍 ТЕСТ С ОТЛАДКОЙ")
print("=" * 60)
print(f"\n📡 Endpoint: {ENDPOINT}")
print(f"🔑 API Key: {API_KEY[:20]}...")
print()

# Тест 1: Прямой запрос через requests
print("1️⃣ Тест прямого запроса через requests:")
print("-" * 60)

payload = {
    "level": "info",
    "message": "Test log from debug script",
    "context": {"test": True, "source": "debug"}
}

try:
    response = requests.post(
        ENDPOINT,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=10.0,
    )
    
    print(f"✅ Статус код: {response.status_code}")
    print(f"📄 Ответ сервера:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    
    if response.status_code in (200, 201):
        print("\n✅ УСПЕХ! Запрос дошел до сервера!")
    elif response.status_code == 401:
        print("\n❌ ОШИБКА 401: Неверный Authorization header")
    elif response.status_code == 403:
        print("\n❌ ОШИБКА 403: Неверный API ключ")
    elif response.status_code == 400:
        print("\n❌ ОШИБКА 400: Неверный формат запроса")
    else:
        print(f"\n⚠️ Неожиданный статус: {response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ ТАЙМАУТ: Сервер не ответил за 10 секунд")
except requests.exceptions.ConnectionError as e:
    print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ: {e}")
except Exception as e:
    print(f"❌ ОШИБКА: {type(e).__name__}: {e}")

print("\n" + "=" * 60)

# Тест 2: Через SDK
print("\n2️⃣ Тест через SDK (обычный режим):")
print("-" * 60)

logger = StraylLogger(
    api_key=API_KEY,
    default_context={"service": "python-test", "env": "local"},
    async_mode=False,  # Синхронный режим для отладки
)

try:
    logger.info("Test log from SDK (debug mode)")
    print("✅ SDK вызван без ошибок")
    print("⚠️ Но SDK проглатывает ошибки, поэтому мы не видим, что произошло")
except Exception as e:
    print(f"❌ ОШИБКА в SDK: {e}")

print("\n" + "=" * 60)

# Тест 3: Проверка доступности endpoint
print("\n3️⃣ Проверка доступности endpoint:")
print("-" * 60)

try:
    # Простой GET запрос (может вернуть 405 Method Not Allowed, но это нормально)
    response = requests.get(ENDPOINT, timeout=5.0)
    print(f"✅ Endpoint доступен (статус: {response.status_code})")
    if response.status_code == 405:
        print("   (405 - это нормально, endpoint принимает только POST)")
except Exception as e:
    print(f"❌ Endpoint недоступен: {e}")

print("\n" + "=" * 60)
print("\n📋 ЧТО ДЕЛАТЬ ДАЛЬШЕ:")
print("1. Если статус 200/201 - запрос работает, проверьте Dashboard → Logs")
print("2. Если статус 401/403 - проверьте API ключ")
print("3. Если таймаут - проверьте интернет-соединение")
print("4. Проверьте логи Edge Function в Supabase Dashboard")
print("   https://supabase.com/dashboard/project/ougtygyvcgdnytkswier/functions/log")
print()

