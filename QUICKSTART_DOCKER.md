# 🚀 Быстрый старт: FL система в Docker

## Один шаг для запуска всей системы

```bash
python scripts/setup-fl-system.py
```

Эта команда:
1. Проверит Docker и Docker Compose
2. Сгенерирует gRPC stubs
3. Соберет Docker images
4. Запустит все сервисы
5. Загрузит базовую модель в MinIO

## Что будет работать после запуска

| Сервис | URL | Логин/Пароль |
|--------|-----|--------------|
| Client API (Swagger) | http://localhost:8000/docs | - |
| MinIO Console | http://localhost:9001 | admin / admin12345 |
| FL Server (gRPC) | localhost:50051 | - |

## Быстрая проверка

```bash
# 1. Проверка Client API
curl http://localhost:8000/health

# 2. Проверка FL Server
curl http://localhost:8080/health

# 3. Просмотр логов
docker-compose logs -f fl-client
```

## Использование с фронтендом

1. Откройте `apps/frontend/demo/index.html` в браузере
2. Делайте свайпы на клавиатуре
3. Нажимайте "Предсказать" для получения предсказания
4. Нажимайте "Запустить обучение FL" для обучения

## Как работает Federated Learning

```
1. Фронтенд → Client: Отправка свайпов
   POST /api/v1/swipes

2. Client: Сохранение в JSONL (data/raw/)

3. Фронтенд → Client: Запуск обучения
   POST /api/v1/train

4. Client → Server: Скачивание глобальной модели
   gRPC GetReleaseWeights() → ссылка на MinIO

5. Client: Локальное обучение на своих данных

6. Client → Server: Отправка дельты
   gRPC AddMyWeights(delta, num_examples)

7. Server: Сохранение дельты в MinIO

8. Server (каждые 5 мин): FedAvg агрегация

9. Server: Сохранение новой глобальной модели

10. Client: Hot reload модели (автоматически!)
```

## Основные команды

```bash
# Просмотр статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f

# Перезапуск сервиса
docker-compose restart fl-client

# Остановка всех сервисов
docker-compose down

# Полная пересборка
docker-compose build
docker-compose up -d
```

## Тестирование API

### Предсказание слова

```bash
curl -X POST http://localhost:8000/api/v1/predict \
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

### Сохранение свайпа

```bash
curl -X POST http://localhost:8000/api/v1/swipes \
  -H "Content-Type: application/json" \
  -d '{
    "gesture_id": "test-002",
    "coords": [
      {"x": 49.5, "y": 84.5, "t": 0.0},
      {"x": 147.5, "y": 84.5, "t": 0.1}
    ],
    "word": "йц"
  }'
```

### Запуск обучения

```bash
curl -X POST http://localhost:8000/api/v1/train
```

### Статистика

```bash
curl http://localhost:8000/api/v1/stats
```

## Troubleshooting

### "Port already in use"

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Контейнер не стартует

```bash
# Просмотр логов
docker-compose logs fl-server

# Пересоздание контейнера
docker-compose up -d --force-recreate fl-server
```

### Модель не найдена

```bash
# Проверка наличия модели
ls apps/client/model2.pt

# Повторная инициализация
python scripts/setup-fl-system.py
```

## Полная документация

- **Детальное руководство**: [`DOCKER_SETUP.md`](DOCKER_SETUP.md)
- **Архитектура клиента**: [`apps/client/NEW_ARCHITECTURE.md`](apps/client/NEW_ARCHITECTURE.md)
- **Quick Start клиента**: [`apps/client/QUICKSTART.md`](apps/client/QUICKSTART.md)

---

**Готово!** Система запущена и работает. 🎉

