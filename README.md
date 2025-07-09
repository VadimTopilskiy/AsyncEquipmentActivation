
# ⚙️ Async Equipment Activation

A microservice-based system for asynchronous activation of telecom equipment using FastAPI, RabbitMQ and Docker.

Микросервисная система для асинхронной активации телеком-оборудования с использованием FastAPI, RabbitMQ и Docker.

---

## 📦 Components / Компоненты

- `service_a`: Mock activation handler
- `service_b`: API gateway for creating and checking tasks
- `worker`: Task executor, consumes from RabbitMQ
- `rabbitmq`: Message broker

---

## 🚀 Run Locally / Локальный запуск

### 📋 Requirements / Требования

- Docker + Docker Compose
- Make (optional, for convenience)

### 🔧 Build and Run / Сборка и запуск

```bash
docker compose build
docker compose up
```

---

## 📋 API Docs / Документация API

Swagger UI доступен по адресу:

- http://localhost:8000/docs

---

## 📡 Example Request / Пример запроса

### POST `/api/v1/equipment/cpe/{id}`

```json
{
  "timeoutInSeconds": 60,
  "parameters": {
    "config": "example"
  }
}
```

Ответ:
```json
{
  "code": 200,
  "taskId": "UUID"
}
```

### GET `/api/v1/equipment/cpe/{id}/task/{task_id}`

Возможные ответы:

- 204 No Content – задача еще выполняется
- 200 OK – задача выполнена успешно
- 500 Internal Server Error – задача завершилась с ошибкой

---

## 🧪 How to Test / Как протестировать

1. Запустите все сервисы:
```bash
docker compose up --build
```

2. Перейдите в браузере по адресу `http://localhost:8000/docs` – это Swagger UI сервиса `service_b`.

3. Отправьте POST-запрос на `/api/v1/equipment/cpe/{id}` (например, `ABC123`) с телом запроса, как указано выше.

4. Скопируйте `taskId` из ответа.

5. Проверьте статус задачи через GET-запрос `/api/v1/equipment/cpe/{id}/task/{task_id}`.

---

## 🐳 Docker Compose Structure

```yaml
services:
  service_a:
  service_b:
  worker:
  rabbitmq:
```

---

## 💬 Notes / Примечания

- Все задачи обрабатываются асинхронно через RabbitMQ.
- Для упрощения проект использует in-memory хранилище задач (можно заменить на Redis/DB).

---
