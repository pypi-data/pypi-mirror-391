# Strayl Logging SDK для TypeScript/JavaScript

Минималистичный TypeScript/JavaScript SDK для отправки логов в Strayl Cortyx через API ключи.

## Установка

```bash
npm install strayl-logging
```

Или с использованием yarn:

```bash
yarn add strayl-logging
```

Или с использованием pnpm:

```bash
pnpm add strayl-logging
```

## Быстрый старт

```typescript
import { StraylLogger } from 'strayl-logging';

// Инициализация логгера
const logger = new StraylLogger({ apiKey: "st_ваш_ключ" });

// Отправка логов
logger.info("Server started", { port: 8000 });
logger.warn("High memory usage", { usage: "85%" });
logger.error("Database connection failed", { retry: true });
logger.debug("Processing request", { request_id: "abc123" });
```

## Получение API ключа

1. Зарегистрируйтесь на [strayl.dev](https://strayl.dev)
2. Перейдите в [Dashboard](https://strayl.dev/dashboard)
3. Откройте вкладку **API**
4. Создайте новый API ключ
5. Скопируйте ключ (формат `st_...`)

## Использование

### Базовое использование

```typescript
import { StraylLogger } from 'strayl-logging';

const logger = new StraylLogger({ apiKey: "st_ваш_ключ" });
logger.info("Application started");
```

### С контекстом по умолчанию

```typescript
const logger = new StraylLogger({
  apiKey: "st_ваш_ключ",
  defaultContext: {
    service: "my-service",
    version: "1.0.0",
    environment: "production",
  },
});

logger.info("User logged in", { user_id: 123 });
// Отправит: { service: "my-service", version: "1.0.0", environment: "production", user_id: 123 }
```

### Синхронный режим

По умолчанию логи отправляются асинхронно. Для синхронной отправки:

```typescript
const logger = new StraylLogger({
  apiKey: "st_ваш_ключ",
  asyncMode: false, // Синхронная отправка
});
```

### Кастомный эндпоинт

```typescript
const logger = new StraylLogger({
  apiKey: "st_ваш_ключ",
  endpoint: "https://custom-endpoint.com/log",
});
```

### Настройка таймаута

```typescript
const logger = new StraylLogger({
  apiKey: "st_ваш_ключ",
  timeout: 5000, // 5 секунд (по умолчанию 3000)
});
```

### Отключение локального вывода

По умолчанию логи выводятся локально через `console` и отправляются на сервер. Чтобы отключить локальный вывод:

```typescript
const logger = new StraylLogger({
  apiKey: "st_ваш_ключ",
  localOutput: false, // Только отправка на сервер, без локального вывода
});
```

## API Reference

### `StraylLogger`

#### Параметры конструктора

```typescript
interface StraylLoggerOptions {
  apiKey: string;              // API ключ для аутентификации (обязательный, формат st_...)
  endpoint?: string;            // URL эндпоинта (по умолчанию используется production endpoint)
  defaultContext?: LogContext;  // Контекст по умолчанию для всех логов
  timeout?: number;             // Таймаут запроса в миллисекундах (по умолчанию 3000)
  asyncMode?: boolean;          // Асинхронная отправка (по умолчанию true)
  localOutput?: boolean;        // Локальный вывод логов через console (по умолчанию true)
}
```

#### Методы

- `info(message: string, context?: LogContext)` - Отправка информационного лога
- `warn(message: string, context?: LogContext)` - Отправка предупреждения
- `error(message: string, context?: LogContext)` - Отправка ошибки
- `debug(message: string, context?: LogContext)` - Отправка отладочного лога
- `log(level: LogLevel, message: string, context?: LogContext)` - Отправка лога с указанным уровнем

#### Типы

```typescript
type LogLevel = "info" | "warn" | "error" | "debug";
type LogContext = Record<string, any>;
```

## Безопасность

- API ключи передаются через заголовок `Authorization: Bearer <api_key>`
- Все запросы выполняются по HTTPS
- Ошибки отправки не ломают приложение (проглатываются молча)
- Логи не содержат чувствительных данных (пароли, токены и т.д.)

## Особенности

- **Двойной вывод**: Логи выводятся локально (через console) и отправляются на сервер
- **Неблокирующий**: По умолчанию логи отправляются асинхронно
- **Безопасный**: Ошибки отправки не ломают приложение
- **Минималистичный**: Один класс, простой API
- **Типизированный**: Полная поддержка TypeScript с типами

## Примеры использования

### В Node.js приложении

```typescript
import { StraylLogger } from 'strayl-logging';

const logger = new StraylLogger({
  apiKey: process.env.STRAYL_API_KEY!,
  defaultContext: { service: "web-app" },
});

logger.info("Server started");
```

### В браузерном приложении

```typescript
import { StraylLogger } from 'strayl-logging';

const logger = new StraylLogger({ apiKey: "st_ваш_ключ" });

// В обработчике события
button.addEventListener('click', () => {
  logger.info("Button clicked", { buttonId: "submit" });
});
```

### В фоновой задаче

```typescript
import { StraylLogger } from 'strayl-logging';

const logger = new StraylLogger({ apiKey: "st_ваш_ключ" });

async function processTask(taskId: string) {
  try {
    logger.info("Task started", { task_id: taskId });
    // ... обработка задачи ...
    logger.info("Task completed", { task_id: taskId });
  } catch (error) {
    logger.error("Task failed", { 
      task_id: taskId, 
      error: error instanceof Error ? error.message : String(error) 
    });
  }
}
```

## Требования

- Node.js >= 14.0.0
- TypeScript >= 5.0.0 (для разработки)

## Лицензия

MIT

## Поддержка

- **GitHub**: [github.com/AlemzhanJ/strayl-sdk-py](https://github.com/AlemzhanJ/strayl-sdk-py)
- **Документация**: [strayl.dev/docs](https://strayl.dev/docs)
- **Dashboard**: [strayl.dev/dashboard](https://strayl.dev/dashboard)
- **Email**: support@strayl.dev

## Разработка

```bash
# Клонировать репозиторий
git clone https://github.com/AlemzhanJ/strayl-sdk-py.git
cd strayl-sdk-py/typescript

# Установить зависимости
npm install

# Собрать проект
npm run build
```

