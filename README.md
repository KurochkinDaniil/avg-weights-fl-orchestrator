# 🔐 Federated Learning для Swipe Keyboard

Полная система федеративного обучения для свайп-клавиатуры с использованием FedAvg алгоритма.

## 📋 Оглавление

- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [Компоненты системы](#компоненты-системы)
- [Документация](#документация)
- [Разработка](#разработка)

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                   FL System Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Frontend (Browser)                                          │
│       │                                                       │
│       ↓ HTTP REST API                                        │
│  ┌──────────────┐         ┌──────────────┐                  │
│  │  FL Client   │────────▶│  FL Server   │                  │
│  │  (Python)    │  gRPC   │  (Golang)    │                  │
│  │  FastAPI     │  :50051 │  gRPC        │                  │
│  │  Port: 8000  │         │  Port: 50051 │                  │
│  └──────────────┘         └──────────────┘                  │
│       │                          │                            │
│       │ JSONL                    │ S3 API                    │
│       ↓                          ↓                            │
│  Local Storage           ┌──────────────┐                    │
│  (data/raw/)             │    MinIO     │                    │
│                          │  Port: 9000  │                    │
│                          └──────────────┘                    │
│                                 │                             │
│                          ┌──────────────┐                    │
│                          │  PostgreSQL  │                    │
│                          │  Port: 5432  │                    │
│                          └──────────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.9+
- Базовая модель `apps/client/model2.pt`

### Запуск системы (1 команда)

```bash
python scripts/setup-fl-system.py
```

Эта команда автоматически:
- ✅ Проверит зависимости
- ✅ Сгенерирует gRPC stubs
- ✅ Соберет Docker images
- ✅ Запустит все сервисы
- ✅ Загрузит базовую модель в MinIO

### Доступные сервисы

| Сервис | URL | Описание |
|--------|-----|----------|
| **Client API** | http://localhost:8000/docs | FastAPI Swagger UI |
| **MinIO Console** | http://localhost:9001 | MinIO Web (admin/admin12345) |
| **FL Server** | localhost:50051 | gRPC endpoint |
| **PostgreSQL** | localhost:5432 | Metadata DB |

### Использование

1. **Откройте фронтенд**: `apps/frontend/demo/index.html`
2. **Делайте свайпы** на клавиатуре
3. **Получайте предсказания**: кнопка "Предсказать"
4. **Запускайте обучение**: кнопка "Запустить обучение FL"

## 🧩 Компоненты системы

### 1. Frontend (Browser)
- **Технологии**: HTML, CSS, JavaScript
- **Библиотека**: SimpleKeyboard + SimpleKeyboardSwipe
- **Функции**: 
  - Отрисовка клавиатуры (1080x631px)
  - Захват свайпов
  - Отправка данных на Client API
  - Отображение предсказаний

### 2. FL Client (Python)
- **Технологии**: FastAPI, PyTorch, gRPC
- **Порт**: 8000
- **Функции**:
  - REST API для фронтенда
  - Сохранение свайпов в JSONL
  - Локальное обучение модели
  - Вычисление дельт весов
  - Отправка дельт на сервер
  - Hot reload модели

**Архитектура**:
- Service Layer (PredictionService, StorageService, TrainingService)
- ModelManager (Singleton, thread-safe)
- Background Tasks (async saving, training)
- Custom Exceptions

### 3. FL Server (Golang)
- **Технологии**: Go, gRPC, MinIO, PostgreSQL
- **Порт**: 50051 (gRPC), 8080 (HTTP health)
- **Функции**:
  - Прием дельт от клиентов (AddMyWeights)
  - Отдача ссылок на глобальную модель (GetReleaseWeights)
  - Периодическая агрегация (FedAvg, каждые 5 минут)
  - Сохранение моделей в MinIO

### 4. MinIO (S3 Storage)
- **Порт**: 9000 (API), 9001 (Console)
- **Bucket**: `fl-models`
- **Структура**:
  - `weights/global/latest.pt` - глобальная модель
  - `weights/clients/{timestamp}_{client_id}.pt` - дельты клиентов

### 5. PostgreSQL
- **Порт**: 5432
- **База**: `fl_metadata`
- **Функции**: Хранение метаданных FL (timestamps, client info)

## 📚 Документация

### Основная документация

- **[QUICKSTART_DOCKER.md](QUICKSTART_DOCKER.md)** - Быстрый старт с Docker
- **[DOCKER_SETUP.md](DOCKER_SETUP.md)** - Полное руководство по Docker
- **[README_DOCKER.md](README_DOCKER.md)** - Краткая справка по Docker

### Документация клиента

- **[apps/client/NEW_ARCHITECTURE.md](apps/client/NEW_ARCHITECTURE.md)** - Архитектура клиента
- **[apps/client/QUICKSTART.md](apps/client/QUICKSTART.md)** - Quick Start клиента
- **[apps/client/FL_TRAINING.md](apps/client/FL_TRAINING.md)** - Обучение FL
- **[apps/client/GPU_SETUP.md](apps/client/GPU_SETUP.md)** - Настройка GPU

## 🔄 Federated Learning Flow

```
1. Frontend → Client: Отправка свайпов
   POST /api/v1/swipes
   
2. Client: Сохранение в JSONL (data/raw/)

3. Frontend → Client: Запуск обучения
   POST /api/v1/train (Background Task)
   
4. Client → Server: Скачивание глобальной модели
   gRPC GetReleaseWeights() → MinIO link
   
5. Client: GET http://minio:9000/fl-models/weights/global/latest.pt

6. Client: Локальное обучение на своих данных
   - Загрузка JSONL
   - Препроцессинг (x, y, dt, vx, vy, ax, ay)
   - Обучение SwipeLSTM
   
7. Client: Вычисление дельты
   delta = local_weights - global_weights
   
8. Client → Server: Отправка дельты
   gRPC AddMyWeights(delta, num_examples)
   
9. Server: Сохранение дельты в MinIO
   weights/clients/{timestamp}_{client_id}.pt
   
10. Server (Cron, каждые 5 мин): FedAvg агрегация
    - Загрузка всех дельт с последней агрегации
    - Weighted averaging
    - Сохранение новой глобальной модели
    
11. Client: Hot reload модели (автоматически!)
    - ModelManager.reload_from_weights()
    - Без перезапуска сервиса!
```

## 🛠️ Разработка

### Локальная разработка клиента (без Docker)

```bash
cd apps/client
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Генерация proto
python scripts/generate-proto-python.py

# Запуск
uvicorn main:app --reload --port 8000
```

### Локальная разработка сервера (без Docker)

```bash
cd apps/server

# Генерация proto
make proto

# Запуск
go run cmd/server/main.go
```

### Изменение кода в Docker

```bash
# После изменения кода клиента
docker-compose build fl-client
docker-compose up -d fl-client

# После изменения кода сервера
docker-compose build fl-server
docker-compose up -d fl-server
```

## 🧪 Тестирование

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Предсказание
curl -X POST http://localhost:8000/api/v1/predict \
  -H "Content-Type: application/json" \
  -d '{"gesture_id":"test","coords":[{"x":49.5,"y":84.5,"t":0.0}],"word":"й"}'

# Сохранение свайпа
curl -X POST http://localhost:8000/api/v1/swipes \
  -H "Content-Type: application/json" \
  -d '{"gesture_id":"test","coords":[{"x":49.5,"y":84.5,"t":0.0}],"word":"й"}'

# Запуск обучения
curl -X POST http://localhost:8000/api/v1/train

# Статистика
curl http://localhost:8000/api/v1/stats
```

### gRPC Testing

```bash
# Установка grpcurl
# Windows: choco install grpcurl
# Mac: brew install grpcurl

# Список сервисов
grpcurl -plaintext localhost:50051 list

# GetReleaseWeights
grpcurl -plaintext -d '{}' localhost:50051 serverside.AvgWeights/GetReleaseWeights
```

## 📊 Мониторинг

```bash
# Просмотр логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f fl-client
docker-compose logs -f fl-server

# Статус контейнеров
docker-compose ps

# Ресурсы
docker stats
```

## 🐛 Troubleshooting

### Порт занят

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Контейнер не стартует

```bash
docker-compose logs fl-server
docker-compose up -d --force-recreate fl-server
```

### Модель не найдена

```bash
# Проверка
docker exec fl-minio mc ls local/fl-models/weights/global/

# Повторная загрузка
python scripts/setup-fl-system.py
```

## 🔒 Production Considerations

### Security
- [ ] Добавить TLS для gRPC
- [ ] Изменить пароли MinIO и PostgreSQL
- [ ] Ограничить CORS на клиенте
- [ ] Добавить аутентификацию для API

### Scaling
- [ ] Horizontal scaling клиентов
- [ ] Load balancer (Nginx)
- [ ] Distributed training

### Monitoring
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Logging aggregation (ELK)
- [ ] Alerting

### Privacy
- [ ] Differential Privacy
- [ ] Secure Aggregation
- [ ] Client anonymization

## 📝 Лицензия

MIT License

## 👥 Авторы

- Federated Learning Server: Golang team
- Federated Learning Client: Python team
- Frontend: JavaScript team

---

**Готово!** 🎉 Полная система федеративного обучения для свайп-клавиатуры.
