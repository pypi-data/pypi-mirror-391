/**
 * Strayl Logging SDK для TypeScript/JavaScript.
 *
 * Минималистичный SDK для отправки логов в Strayl Cortyx через API ключи.
 */

export { StraylLogger } from "./client";
export type {
  LogLevel,
  LogContext,
  StraylLoggerOptions,
} from "./client";

// Версия пакета
export const VERSION = "0.2.0";

