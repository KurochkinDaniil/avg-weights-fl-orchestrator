# 🐳 Docker Setup: Full FL System

## Архитектура системы

```
┌─────────────────────────────────────────────────────────────┐
│                     FL System Architecture                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐         ┌──────────────┐                 │
│  │  FL Client   │────────▶│  FL Server   │                 │
│  │ (Python)     │  gRPC   │ (Go)         │                 │
│  │ Port: 8000   │  :50051 │ Port: 50051  │                 │
│  └──────────────┘         └──────────────┘                 │
│         │                         │                          │
│         │                         ▼                          │
│         │                  ┌──────────────┐                 │
│         │                  │    MinIO     │                 │
│         │                  │ Port: 9000   │                 │
│         └─────────────────▶│ (S3 storage) │                 │
│                             └──────────────┘                 │
│                                    │                         │
│                             ┌──────────────┐                 │
│                             │  PostgreSQL  │                 │
│                             │ Port: 5432   │                 │
│                             └──────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

## Компоненты

| Сервис | Порт | Описание |
|--------|------|----------|
| **fl-client** | 8000 | Python FastAPI (predictions, data collection) |
| **fl-server** | 50051 | Go gRPC server (federated aggregation) |
| **minio** | 9000, 9001 | S3-compatible storage для моделей |
| **postgres** | 5432 | Metadata database |

## 🚀 Quick Start

### Шаг 1: Подготовка

```bash
# 1. Убедитесь, что Docker и Docker Compose установлены
docker --version
docker-compose --version

# 2. Убедитесь, что базовая модель существует
ls apps/client/model2.pt  # Должен быть файл

# 3. Инициализируйте сервер базовой моделью
bash scripts/init-server-model.sh
```

### Шаг 2: Запуск всей системы

```bash
# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Или отдельно:
docker-compose logs -f fl-server
docker-compose logs -f fl-client
```

### Шаг 3: Проверка

```bash
# 1. Проверка MinIO
curl http://localhost:9001  # MinIO Console (admin/admin12345)

# 2. Проверка FL Server
curl http://localhost:8080/health

# 3. Проверка FL Client
curl http://localhost:8000/health

# 4. Проверка gRPC
grpcurl -plaintext localhost:50051 list
```

## 📊 Использование системы

### 1. Сохранение свайпа (через клиент)

```bash
curl -X POST http://localhost:8000/api/v1/swipes \
  -H "Content-Type: application/json" \
  -d '{
    "gesture_id": "test-001",
    "coords": [
      {"x": 49.5, "y": 84.5, "t": 0.0},
      {"x": 147.5, "y": 84.5, "t": 0.1}
    ],
    "word": "йц"
  }'
```

### 2. Запуск обучения (в фоне)

```bash
curl -X POST http://localhost:8000/api/v1/train

# Response:
{
  "status": "training_started",
  "message": "Federated learning training cycle started in background"
}
```

### 3. Процесс FL:

```
Client:
1. POST /train
   ↓
2. gRPC GetReleaseWeights() → получить ссылку на MinIO
   ↓
3. GET http://minio:9000/fl-models/weights/global/latest.pt
   ↓
4. Обучение локально на данных
   ↓
5. gRPC AddMyWeights(delta) → отправка дельты на сервер
   
Server:
6. Сохранение дельты в MinIO
   ↓
7. Cron (каждые 5 минут): FedAvg aggregation
   ↓
8. Сохранение новой глобальной модели в MinIO
   
Client:
9. Hot reload модели (без перезапуска!)
```

## 🔧 Управление

### Просмотр статуса

```bash
# Все контейнеры
docker-compose ps

# Логи
docker-compose logs -f fl-server
docker-compose logs -f fl-client

# Ресурсы
docker stats
```

### Перезапуск сервиса

```bash
# Один сервис
docker-compose restart fl-client

# Все сервисы
docker-compose restart
```

### Остановка

```bash
# Остановить все
docker-compose down

# Остановить и удалить volumes (ОСТОРОЖНО: удалит данные!)
docker-compose down -v
```

### Обновление кода

```bash
# После изменения кода:
docker-compose build fl-client
docker-compose up -d fl-client

# Или rebuild всё:
docker-compose build
docker-compose up -d
```

## 📁 Volumes (persistent data)

| Volume | Содержимое |
|--------|-----------|
| `minio_data` | Модели и дельты в MinIO |
| `postgres_data` | Метаданные FL |
| `server_models` | Кэш моделей на сервере |
| `client_data` | JSONL файлы со свайпами |
| `client_models` | Локальные модели клиента |

## 🔍 Debugging

### Проверка сети

```bash
# Список сетей
docker network ls

# Проверка подключений
docker network inspect avg-weights-fl-orchestrator_fl-network
```

### Проверка MinIO

```bash
# Открыть MinIO Console
open http://localhost:9001
# Login: admin / admin12345

# Или через CLI
docker exec fl-minio mc ls local/fl-models/weights/global/
```

### Проверка базы данных

```bash
# Подключение к PostgreSQL
docker exec -it fl-postgres psql -U fluser -d fl_metadata

# SQL запросы
\dt  # Список таблиц
SELECT * FROM metadata;
```

### Тестирование gRPC

```bash
# Установить grpcurl (если нет)
# brew install grpcurl  # Mac
# choco install grpcurl  # Windows

# Список сервисов
grpcurl -plaintext localhost:50051 list

# Вызов GetReleaseWeights
grpcurl -plaintext -d '{}' localhost:50051 serverside.AvgWeights/GetReleaseWeights

# Вызов AddMyWeights (пример)
grpcurl -plaintext -d '{
  "client_id": "test",
  "weights": "dGVzdA==",
  "num_examples": 10
}' localhost:50051 serverside.AvgWeights/AddMyWeights
```

## 🐛 Troubleshooting

### Ошибка: "Cannot connect to server"

```bash
# Проверьте, что сервер запущен
docker-compose ps fl-server

# Проверьте логи
docker-compose logs fl-server

# Перезапустите
docker-compose restart fl-server
```

### Ошибка: "Model not found in MinIO"

```bash
# Проверьте наличие модели
docker exec fl-minio mc ls local/fl-models/weights/global/

# Если нет, инициализируйте
bash scripts/init-server-model.sh
docker-compose restart fl-server
```

### Ошибка: "Port already in use"

```bash
# Найти процесс на порту
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Изменить порты в docker-compose.yml
```

### Контейнер не стартует

```bash
# Проверить зависимости
docker-compose up --no-start
docker-compose start

# Пересоздать контейнер
docker-compose up -d --force-recreate fl-client
```

## 🔒 Production Considerations

### Security

1. **Изменить пароли MinIO**:
```yaml
environment:
  MINIO_ROOT_USER: your-secure-user
  MINIO_ROOT_PASSWORD: your-secure-password-32chars
```

2. **Добавить TLS для gRPC**:
```yaml
environment:
  - GRPC_TLS_ENABLED=true
  - GRPC_TLS_CERT=/certs/server.crt
  - GRPC_TLS_KEY=/certs/server.key
```

3. **Ограничить CORS на клиенте**:
```python
# main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],  # Точные origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Scaling

```bash
# Масштабирование клиентов
docker-compose up -d --scale fl-client=3

# Load balancer перед клиентами
# Добавить nginx в docker-compose.yml
```

### Monitoring

```bash
# Добавить Prometheus + Grafana
# См. docker-compose.monitoring.yml
```

## 📚 Документация

- **Client API**: http://localhost:8000/docs (FastAPI Swagger)
- **MinIO Console**: http://localhost:9001
- **Архитектура клиента**: `apps/client/NEW_ARCHITECTURE.md`
- **Quick Start клиента**: `apps/client/QUICKSTART.md`

## ✅ Checklist

- [ ] Docker и Docker Compose установлены
- [ ] Базовая модель `apps/client/model2.pt` существует
- [ ] Запущен `scripts/init-server-model.sh`
- [ ] Запущен `docker-compose up -d`
- [ ] Все контейнеры healthy: `docker-compose ps`
- [ ] MinIO доступен: http://localhost:9001
- [ ] Client API доступен: http://localhost:8000/docs
- [ ] Server gRPC доступен: `grpcurl -plaintext localhost:50051 list`

## 🎉 Готово!

Теперь у вас полностью работающая Federated Learning система в Docker!

Для начала работы:
1. Откройте фронтенд: `apps/frontend/demo/index.html`
2. Делайте свайпы и сохраняйте их
3. Запускайте обучение: `curl -X POST http://localhost:8000/api/v1/train`
4. Модель обновится автоматически!

