/**
 * Клиент для отправки логов в Strayl Cortyx.
 *
 * Этот модуль предоставляет класс StraylLogger для отправки логов
 * через API ключи в централизованное хранилище Strayl.
 */

/**
 * Уровни логов
 */
export type LogLevel = "info" | "warn" | "error" | "debug";

/**
 * Контекст лога - объект с произвольными ключами
 */
export type LogContext = Record<string, any>;

/**
 * Опции для инициализации StraylLogger
 */
export interface StraylLoggerOptions {
  /**
   * API ключ для аутентификации (обязательный, формат st_...)
   */
  apiKey: string;
  /**
   * URL эндпоинта (по умолчанию используется production endpoint)
   */
  endpoint?: string;
  /**
   * Контекст по умолчанию для всех логов
   */
  defaultContext?: LogContext;
  /**
   * Таймаут запроса в миллисекундах (по умолчанию 3000)
   */
  timeout?: number;
  /**
   * Если true, отправка выполняется асинхронно (по умолчанию true)
   */
  asyncMode?: boolean;
  /**
   * Если true, логи выводятся локально через console (по умолчанию true)
   */
  localOutput?: boolean;
}

/**
 * Payload для отправки лога
 */
interface LogPayload {
  level: LogLevel;
  message: string;
  context: LogContext;
}

/**
 * Минималистичный TypeScript логгер для Strayl Cortyx.
 *
 * Отправляет логи через API ключи в централизованное хранилище.
 * Логи не должны ломать приложение пользователя, поэтому все ошибки
 * отправки логируются молча.
 *
 * @example
 * ```typescript
 * import { StraylLogger } from 'strayl-logging';
 *
 * const logger = new StraylLogger({ apiKey: "st_..." });
 * logger.info("Server started", { port: 8000 });
 * logger.error("Connection failed", { retry: true });
 * ```
 */
export class StraylLogger {
  /**
   * URL эндпоинта по умолчанию
   */
  private static readonly DEFAULT_ENDPOINT =
    "https://ougtygyvcgdnytkswier.supabase.co/functions/v1/log";

  /**
   * Поддерживаемые уровни логов
   */
  private static readonly VALID_LEVELS: Set<LogLevel> = new Set([
    "info",
    "warn",
    "error",
    "debug",
  ]);

  /**
   * API ключ для аутентификации
   */
  public readonly apiKey: string;

  /**
   * URL эндпоинта для отправки логов
   */
  public readonly endpoint: string;

  /**
   * Контекст по умолчанию для всех логов
   */
  public readonly defaultContext: LogContext;

  /**
   * Таймаут запроса в миллисекундах
   */
  public readonly timeout: number;

  /**
   * Если true, отправка выполняется асинхронно
   */
  public readonly asyncMode: boolean;

  /**
   * Если true, логи выводятся локально через console
   */
  public readonly localOutput: boolean;

  /**
   * Инициализация StraylLogger.
   *
   * @param options - Опции для инициализации логгера
   * @throws {Error} Если apiKey не указан или не начинается с 'st_'
   */
  constructor(options: StraylLoggerOptions) {
    const {
      apiKey,
      endpoint,
      defaultContext,
      timeout,
      asyncMode,
      localOutput,
    } = options;

    if (!apiKey) {
      throw new Error("StraylLogger: apiKey is required");
    }

    if (!apiKey.startsWith("st_")) {
      throw new Error(
        "StraylLogger: apiKey must start with 'st_' prefix. " +
          "Get your API key from https://strayl.dev/dashboard"
      );
    }

    this.apiKey = apiKey;
    this.endpoint = endpoint || StraylLogger.DEFAULT_ENDPOINT;
    this.defaultContext = defaultContext || {};
    this.timeout = timeout || 3000;
    this.asyncMode = asyncMode !== false; // По умолчанию true
    this.localOutput = localOutput !== false; // По умолчанию true
  }

  /**
   * Внутренний метод для отправки лога на сервер.
   *
   * @param level - Уровень лога (info, warn, error, debug)
   * @param message - Текст сообщения
   * @param context - Дополнительный контекст для лога
   *
   * @remarks
   * Все ошибки отправки проглатываются, чтобы не ломать приложение.
   */
  private async _send(
    level: LogLevel,
    message: string,
    context?: LogContext
  ): Promise<void> {
    // Валидация уровня
    const validLevel: LogLevel = StraylLogger.VALID_LEVELS.has(level)
      ? level
      : "info"; // Fallback на info при неверном уровне

    // Формирование payload
    const payload: LogPayload = {
      level: validLevel,
      message,
      context: { ...this.defaultContext, ...(context || {}) },
    };

    try {
      // Создаем AbortController для таймаута
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(this.endpoint, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Проверка статуса ответа (не бросаем исключение, только логируем)
      if (response.status !== 200 && response.status !== 201) {
        // В production можно добавить логирование через console.debug
      }
    } catch (error) {
      // Все ошибки (таймаут, сеть, и т.д.) - проглатываем
      // Логгер не должен ломать приложение пользователя
    }
  }

  /**
   * Локальный вывод лога в консоль.
   *
   * @param level - Уровень лога
   * @param message - Текст сообщения
   * @param context - Дополнительный контекст
   */
  private _printLog(
    level: LogLevel,
    message: string,
    context?: LogContext
  ): void {
    if (!this.localOutput) {
      return;
    }

    // Формируем полный контекст
    const fullContext = { ...this.defaultContext, ...(context || {}) };

    // Формируем строку для вывода
    const prefix = `[${level.toUpperCase()}]`;
    const logMessage = `${prefix} ${message}`;

    // Выводим в зависимости от уровня
    switch (level) {
      case "error":
        if (Object.keys(fullContext).length > 0) {
          console.error(logMessage, fullContext);
        } else {
          console.error(logMessage);
        }
        break;
      case "warn":
        if (Object.keys(fullContext).length > 0) {
          console.warn(logMessage, fullContext);
        } else {
          console.warn(logMessage);
        }
        break;
      case "debug":
        if (Object.keys(fullContext).length > 0) {
          console.debug(logMessage, fullContext);
        } else {
          console.debug(logMessage);
        }
        break;
      default: // info
        if (Object.keys(fullContext).length > 0) {
          console.log(logMessage, fullContext);
        } else {
          console.log(logMessage);
        }
        break;
    }
  }

  /**
   * Отправка лога с указанным уровнем.
   *
   * @param level - Уровень лога (info, warn, error, debug)
   * @param message - Текст сообщения
   * @param context - Дополнительный контекст (объединяется с defaultContext)
   *
   * @example
   * ```typescript
   * logger.log("info", "User logged in", { user_id: 123 });
   * ```
   */
  public log(level: LogLevel, message: string, context?: LogContext): void {
    // Сначала выводим локально
    this._printLog(level, message, context);

    // Затем отправляем на сервер
    if (this.asyncMode) {
      // Асинхронная отправка (не ждем завершения)
      this._send(level, message, context).catch(() => {
        // Игнорируем ошибки
      });
    } else {
      // Синхронная отправка (блокирующая, но все равно не ждем в async контексте)
      this._send(level, message, context).catch(() => {
        // Игнорируем ошибки
      });
    }
  }

  /**
   * Отправка информационного лога.
   *
   * @param message - Текст сообщения
   * @param context - Дополнительный контекст
   *
   * @example
   * ```typescript
   * logger.info("Server started", { port: 8000 });
   * ```
   */
  public info(message: string, context?: LogContext): void {
    this.log("info", message, context);
  }

  /**
   * Отправка предупреждения.
   *
   * @param message - Текст сообщения
   * @param context - Дополнительный контекст
   *
   * @example
   * ```typescript
   * logger.warn("High memory usage", { usage: "85%" });
   * ```
   */
  public warn(message: string, context?: LogContext): void {
    this.log("warn", message, context);
  }

  /**
   * Отправка ошибки.
   *
   * @param message - Текст сообщения
   * @param context - Дополнительный контекст
   *
   * @example
   * ```typescript
   * logger.error("Database connection failed", { retry: true });
   * ```
   */
  public error(message: string, context?: LogContext): void {
    this.log("error", message, context);
  }

  /**
   * Отправка отладочного лога.
   *
   * @param message - Текст сообщения
   * @param context - Дополнительный контекст
   *
   * @example
   * ```typescript
   * logger.debug("Processing request", { request_id: "abc123" });
   * ```
   */
  public debug(message: string, context?: LogContext): void {
    this.log("debug", message, context);
  }
}

