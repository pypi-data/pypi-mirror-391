# 🔧 Исправление Edge Function `log`

## Проблема

Edge Function возвращает `401 Invalid JWT` вместо проверки API ключей.

## Причина

Функция `log` не проверяет API ключи, а только JWT токены.

## Решение

Нужно задеплоить правильную версию функции, которая:
1. Проверяет, начинается ли токен с `st_` (API ключ)
2. Если да - использует `verifyApiKey` для проверки
3. Если нет - проверяет как JWT

---

## Код правильной Edge Function

```typescript
// supabase/functions/log/index.ts

import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// Функция для проверки API ключа
async function verifyApiKey(token: string): Promise<string | null> {
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  
  const supabase = createClient(supabaseUrl, supabaseServiceKey);
  
  // Хэшируем ключ
  const encoder = new TextEncoder();
  const data = encoder.encode(token);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
  
  // Ищем в базе
  const { data: keyData, error } = await supabase
    .from("strayl_api_keys")
    .select("user_id")
    .eq("key_hash", hashHex)
    .single();
  
  if (error || !keyData) {
    return null;
  }
  
  return keyData.user_id;
}

Deno.serve(async (req) => {
  // CORS headers
  if (req.method === "OPTIONS") {
    return new Response(null, {
      headers: {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Authorization, Content-Type",
      },
    });
  }

  // Проверка метода
  if (req.method !== "POST") {
    return new Response(
      JSON.stringify({ error: "Method not allowed" }),
      { status: 405, headers: { "Content-Type": "application/json" } }
    );
  }

  // Получаем токен из заголовка
  const authHeader = req.headers.get("Authorization");
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return new Response(
      JSON.stringify({ error: "Missing or invalid Authorization header" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  const token = authHeader.replace("Bearer ", "");
  let userId: string | null = null;

  // Проверяем тип токена
  if (token.startsWith("st_")) {
    // API ключ
    userId = await verifyApiKey(token);
    if (!userId) {
      return new Response(
        JSON.stringify({ error: "Forbidden - Invalid API key" }),
        { status: 403, headers: { "Content-Type": "application/json" } }
      );
    }
  } else if (token.startsWith("eyJ")) {
    // JWT токен
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseAnonKey);
    
    const { data: { user }, error } = await supabase.auth.getUser(token);
    if (error || !user) {
      return new Response(
        JSON.stringify({ error: "Invalid JWT" }),
        { status: 401, headers: { "Content-Type": "application/json" } }
      );
    }
    userId = user.id;
  } else {
    return new Response(
      JSON.stringify({ error: "Invalid token format" }),
      { status: 401, headers: { "Content-Type": "application/json" } }
    );
  }

  // Парсим тело запроса
  let body;
  try {
    body = await req.json();
  } catch {
    return new Response(
      JSON.stringify({ error: "Invalid JSON" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  // Валидация
  if (!body.message || typeof body.message !== "string") {
    return new Response(
      JSON.stringify({ error: "Missing or invalid message field" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const level = body.level || "info";
  const validLevels = ["info", "warn", "error", "debug"];
  if (!validLevels.includes(level)) {
    return new Response(
      JSON.stringify({ error: "Invalid level. Must be one of: info, warn, error, debug" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  // Сохраняем лог в базу
  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseServiceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const supabase = createClient(supabaseUrl, supabaseServiceKey);

  const { data: logData, error: insertError } = await supabase
    .from("strayl_logs")
    .insert({
      user_id: userId,
      level: level,
      message: body.message,
      context: body.context || {},
    })
    .select("id, created_at")
    .single();

  if (insertError) {
    console.error("Error inserting log:", insertError);
    return new Response(
      JSON.stringify({ error: "Internal server error" }),
      { status: 500, headers: { "Content-Type": "application/json" } }
    );
  }

  return new Response(
    JSON.stringify({
      success: true,
      log_id: logData.id,
      created_at: logData.created_at,
    }),
    {
      status: 201,
      headers: {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
      },
    }
  );
});
```

---

## Как задеплоить

### Через Supabase CLI:

```bash
# 1. Создайте файл supabase/functions/log/index.ts с кодом выше

# 2. Задеплойте функцию
supabase functions deploy log
```

### Через Supabase Dashboard:

1. Откройте [Supabase Dashboard](https://supabase.com/dashboard/project/ougtygyvcgdnytkswier/functions)
2. Найдите функцию `log`
3. Нажмите "Edit" или "Deploy"
4. Вставьте код выше
5. Сохраните и задеплойте

---

## Проверка после деплоя

После деплоя запустите снова:

```bash
python test_debug.py
```

Должен вернуться статус `200` или `201` вместо `401`.

---

## Альтернатива: Использовать существующую функцию `logs-test`

Если функция `log` не работает, можно временно использовать `logs-test`:

```python
# В client.py измените DEFAULT_ENDPOINT на:
DEFAULT_ENDPOINT = "https://ougtygyvcgdnytkswier.supabase.co/functions/v1/logs-test"
```

Но лучше исправить функцию `log`.

