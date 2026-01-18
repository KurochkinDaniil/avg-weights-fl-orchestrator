# 🚀 Quick Start: FL System with Docker

## TL;DR - Быстрый запуск (1 команда)

```bash
# Полная установка и запуск системы
python scripts/setup-fl-system.py
```

Это автоматически:
- ✅ Проверит Docker и Docker Compose
- ✅ Сгенерирует gRPC stubs для Python
- ✅ Соберет Docker images
- ✅ Запустит все сервисы (MinIO, PostgreSQL, FL Server, FL Client)
- ✅ Загрузит базовую модель в MinIO

## Доступные сервисы

После запуска:

| Сервис | URL | Описание |
|--------|-----|----------|
| **Client API** | http://localhost:8000/docs | FastAPI Swagger UI |
| **MinIO Console** | http://localhost:9001 | MinIO Web UI (admin/admin12345) |
| **FL Server (gRPC)** | localhost:50051 | gRPC endpoint |
| **PostgreSQL** | localhost:5432 | Database |

## Основные команды

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f fl-server
docker-compose logs -f fl-client
```

### Управление

```bash
# Остановить все
docker-compose down

# Перезапустить сервис
docker-compose restart fl-client

# Пересобрать после изменения кода
docker-compose build fl-client
docker-compose up -d fl-client
```

### Тестирование

```bash
# Проверка Client API
curl http://localhost:8000/health

# Проверка FL Server
curl http://localhost:8080/health

# Предсказание
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gesture_id": "test",
    "coords": [
      {"x": 49.5, "y": 84.5, "t": 0.0},
      {"x": 147.5, "y": 84.5, "t": 0.1}
    ],
    "word": "йц"
  }'

# Запуск обучения
curl -X POST http://localhost:8000/api/v1/train
```

## Использование фронтенда

1. Откройте в браузере: `apps/frontend/demo/index.html`
2. Убедитесь, что в `main.js` API URL указан как `http://localhost:8000`
3. Делайте свайпы на клавиатуре
4. Нажимайте "Предсказать" для получения предсказания
5. Нажимайте "Запустить обучение FL" для запуска цикла обучения

## Архитектура

```
Frontend (Browser)
    ↓ HTTP
FL Client (Python FastAPI) :8000
    ↓ gRPC :50051
FL Server (Go)
    ↓ S3 API :9000
MinIO (Object Storage)
```

## Federated Learning Flow

1. **Client** собирает данные свайпов → сохраняет в JSONL
2. **Client** запускает обучение (POST /train)
3. **Client** → **Server**: скачивает глобальную модель (gRPC GetReleaseWeights)
4. **Client** обучает модель локально на своих данных
5. **Client** вычисляет дельту (local_weights - global_weights)
6. **Client** → **Server**: отправляет дельту (gRPC AddMyWeights)
7. **Server**: сохраняет дельту в MinIO
8. **Server** (cron каждые 5 мин): агрегирует дельты через FedAvg
9. **Server**: сохраняет новую глобальную модель в MinIO
10. **Client**: hot reload модели (без перезапуска!)

## Troubleshooting

### Ошибка: "Port already in use"

```bash
# Найти процесс
netstat -ano | findstr :8000

# Остановить контейнеры
docker-compose down
```

### Модель не найдена в MinIO

```bash
# Проверить наличие
docker exec fl-minio mc ls local/fl-models/weights/global/

# Загрузить вручную
python scripts/setup-fl-system.py  # Выполнит только загрузку
```

### Контейнер не стартует

```bash
# Посмотреть логи
docker-compose logs fl-server

# Пересоздать
docker-compose up -d --force-recreate fl-server
```

### gRPC ошибка: "Proto files not generated"

```bash
# Сгенерировать proto вручную
python scripts/generate-proto-python.py

# Перезапустить клиент
docker-compose restart fl-client
```

## Документация

- **Полное руководство Docker**: [`DOCKER_SETUP.md`](DOCKER_SETUP.md)
- **Архитектура клиента**: [`apps/client/NEW_ARCHITECTURE.md`](apps/client/NEW_ARCHITECTURE.md)
- **Quick Start клиента**: [`apps/client/QUICKSTART.md`](apps/client/QUICKSTART.md)

## Разработка

### Изменение кода клиента

```bash
# 1. Внести изменения в apps/client/
# 2. Пересобрать
docker-compose build fl-client
docker-compose up -d fl-client
```

### Изменение кода сервера

```bash
# 1. Внести изменения в apps/server/
# 2. Пересобрать
docker-compose build fl-server
docker-compose up -d fl-server
```

### Hot reload (без Docker)

Для быстрой разработки можно запускать клиент локально:

```bash
cd apps/client
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate-proto-python.py
uvicorn main:app --reload --port 8000
```

## Production

Для production используйте:
- TLS для gRPC
- Secure passwords для MinIO и PostgreSQL
- Reverse proxy (Nginx) перед сервисами
- Monitoring (Prometheus + Grafana)
- Proper logging

См. [`DOCKER_SETUP.md`](DOCKER_SETUP.md) для деталей.

---

**Готово!** 🎉 Система работает и готова к использованию.

