# 🐳 Docker Setup

## Быстрый старт

### 1. Только клиент (для разработки)

```bash
docker-compose -f docker-compose.dev.yml up
```

- Frontend: http://localhost:3000
- API: http://localhost:8000

### 2. Полная система (с сервером)

```bash
docker-compose up
```

- Frontend: http://localhost:3000
- Client API: http://localhost:8000
- Server gRPC: localhost:50051
- MinIO: http://localhost:9001 (admin/admin12345)

---

## Команды

### Запуск

```bash
# Запустить в фоне
docker-compose up -d

# Посмотреть логи
docker-compose logs -f

# Только клиент
docker-compose -f docker-compose.dev.yml up -d
```

### Остановка

```bash
# Остановить
docker-compose down

# Остановить и удалить volumes
docker-compose down -v
```

### Пересборка

```bash
# Пересобрать после изменений
docker-compose build

# Пересобрать и запустить
docker-compose up --build
```

---

## Обучение в Docker

```bash
# Войти в контейнер клиента
docker exec -it fl-client bash

# Запустить обучение
python scripts/federated_cycle.py

# Выйти
exit
```

---

## Проверка

```bash
# Проверить что контейнеры работают
docker-compose ps

# Логи конкретного сервиса
docker-compose logs client
docker-compose logs server

# Health check
curl http://localhost:8000/health
```

---

## Данные

### Где хранятся данные:

- **Свайпы**: `./apps/client/data/` (примонтирован в контейнер)
- **MinIO**: Docker volume `minio_data`
- **PostgreSQL**: Docker volume `postgres_data`

### Бэкап данных:

```bash
# Экспорт данных
docker cp fl-client:/app/data ./backup/

# Импорт данных
docker cp ./backup/data fl-client:/app/
```

---

## Troubleshooting

### Порт занят

```bash
# Найти процесс
lsof -ti:8000

# Убить
lsof -ti:8000 | xargs kill -9
```

### Пересоздать всё

```bash
# Удалить всё
docker-compose down -v
docker system prune -a

# Запустить заново
docker-compose up --build
```

### Посмотреть логи ошибок

```bash
docker-compose logs --tail=50 client
docker-compose logs --tail=50 server
```

---

## Разработка

### Hot reload для клиента:

```bash
# Использовать dev compose
docker-compose -f docker-compose.dev.yml up

# Изменения в apps/client/ применяются автоматически
```

### Запустить только сервер:

```bash
docker-compose up postgres minio server
```

### Запустить только клиент:

```bash
docker-compose up client frontend
```
