# 🚀 Быстрый старт с Strayl Logging SDK

## Шаг 1: Получение API ключа

### Через Dashboard (рекомендуется):

1. Откройте [Dashboard](https://strayl.dev/dashboard)
2. Войдите в систему
3. Перейдите на вкладку **API**
4. Введите имя ключа (например, "My App Key")
5. Нажмите **GENERATE**
6. **ВАЖНО:** Скопируйте ключ сразу! Он показывается только один раз
7. Сохраните ключ в безопасном месте (например, в `.env` файле)

### Через API (альтернатива):

```bash
curl -X POST "https://ougtygyvcgdnytkswier.supabase.co/functions/v1/generate-api-key" \
  -H "Authorization: Bearer <ваш_jwt_токен>" \
  -H "Content-Type: application/json" \
  -d '{"name": "My App Key"}'
```

---

## Шаг 2: Установка SDK

### Вариант A: Локальная установка (для разработки)

```bash
cd SDK/strayl_logging
pip install -e .
```

### Вариант B: Установка из PyPI (когда опубликуем)

```bash
pip install strayl-logging
```

---

## Шаг 3: Базовое использование

### Простейший пример:

```python
from strayl_logging import StraylLogger

# Инициализация
logger = StraylLogger(api_key="st_ваш_ключ")

# Отправка логов
logger.info("Application started")
logger.warn("High memory usage detected")
logger.error("Database connection failed")
logger.debug("Processing request #123")
```

### С контекстом:

```python
from strayl_logging import StraylLogger

logger = StraylLogger(
    api_key="st_ваш_ключ",
    default_context={
        "service": "my-service",
        "version": "1.0.0",
        "environment": "production",
    },
)

# Лог с дополнительным контекстом
logger.info("User logged in", {"user_id": 123, "ip": "192.168.1.1"})
```

---

## Шаг 4: Тестирование

### Локальный тест:

**Способ 1: Прямо в коде (быстро для теста):**

1. Откройте `test.py` в редакторе
2. Найдите строку 19: `API_KEY = "st_ТВОЙ_КЛЮЧ"`
3. Замените `"st_ТВОЙ_КЛЮЧ"` на ваш реальный API ключ
4. Сохраните файл
5. Запустите:

```bash
cd SDK/strayl_logging
python test.py
```

**Способ 2: Через переменную окружения (безопаснее):**

1. Создайте файл `.env` в папке `SDK/strayl_logging/`
2. Добавьте строку: `STRAYL_API_KEY=st_ваш_ключ`
3. Установите: `pip install python-dotenv`
4. Запустите: `python test_with_env.py`

### Ожидаемый результат:

```
Отправка тестовых логов...
Логи отправлены! Проверьте их в Dashboard: https://strayl.dev/dashboard
```

---

## Шаг 5: Проверка результатов

1. Откройте [Dashboard](https://strayl.dev/dashboard)
2. Перейдите на вкладку **Logs**
3. Обновите страницу (F5)
4. Вы должны увидеть ваши логи с правильными уровнями и контекстом

---

## Шаг 6: Интеграция в ваше приложение

### Пример для Flask:

```python
from flask import Flask
from strayl_logging import StraylLogger
import os

app = Flask(__name__)
logger = StraylLogger(
    api_key=os.getenv("STRAYL_API_KEY"),
    default_context={"service": "flask-app"},
)

@app.route("/")
def index():
    logger.info("Homepage accessed")
    return "Hello World"

@app.errorhandler(500)
def handle_error(e):
    logger.error("Internal server error", {"error": str(e)})
    return "Error", 500
```

### Пример для Django:

```python
# settings.py
import os
from strayl_logging import StraylLogger

STRAYL_LOGGER = StraylLogger(
    api_key=os.getenv("STRAYL_API_KEY"),
    default_context={"service": "django-app"},
)

# views.py
from django.conf import settings

def my_view(request):
    settings.STRAYL_LOGGER.info("View accessed", {"path": request.path})
    return HttpResponse("OK")
```

### Пример для фоновой задачи:

```python
from strayl_logging import StraylLogger

logger = StraylLogger(api_key="st_ваш_ключ")

def process_task(task_id):
    try:
        logger.info("Task started", {"task_id": task_id})
        # ... обработка задачи ...
        logger.info("Task completed", {"task_id": task_id})
    except Exception as e:
        logger.error("Task failed", {"task_id": task_id, "error": str(e)})
```

---

## 🔒 Безопасность

### ✅ Рекомендации:

1. **Никогда не коммитьте API ключи в Git:**
   ```bash
   # Добавьте в .gitignore
   .env
   *.key
   ```

2. **Используйте переменные окружения:**
   ```python
   import os
   logger = StraylLogger(api_key=os.getenv("STRAYL_API_KEY"))
   ```

3. **Разные ключи для разных окружений:**
   - Development: `st_dev_...`
   - Production: `st_prod_...`

---

## 🐛 Решение проблем

### Ошибка: "api_key is required"
- **Причина:** Не передан API ключ
- **Решение:** Убедитесь, что передаете ключ в конструктор

### Ошибка: "api_key must start with 'st_'"
- **Причина:** Неверный формат ключа
- **Решение:** Проверьте, что ключ начинается с `st_`

### Логи не появляются в Dashboard
- **Причина:** Проблема с сетью или неверный ключ
- **Решение:**
  1. Проверьте интернет-соединение
  2. Убедитесь, что ключ правильный
  3. Проверьте логи Edge Function в Supabase Dashboard

### Timeout ошибки
- **Причина:** Медленное соединение
- **Решение:** Увеличьте таймаут:
  ```python
  logger = StraylLogger(
      api_key="st_ваш_ключ",
      timeout=10.0,  # 10 секунд вместо 3
  )
  ```

---

## 📚 Дополнительные ресурсы

- **Полная документация:** `README.md`
- **Техническая спецификация:** `../SDK_SPEC.md`
- **Примеры использования:** `test.py`
- **Dashboard:** https://strayl.dev/dashboard

---

## ✅ Чеклист первого запуска

- [ ] Получен API ключ через Dashboard
- [ ] SDK установлен локально (`pip install -e .`)
- [ ] Запущен `test.py` с реальным ключом
- [ ] Логи появились в Dashboard → вкладка **Logs**
- [ ] SDK интегрирован в приложение
- [ ] API ключ сохранен в переменных окружения

---

**Готово! Теперь вы можете использовать Strayl Logging SDK в своих проектах! 🎉**

