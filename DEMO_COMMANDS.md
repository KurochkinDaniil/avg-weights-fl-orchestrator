# 🎬 Команды для демонстрации FL системы

## ✅ Система успешно настроена!

Все контейнеры работают, модель в MinIO загружена, оба клиента успешно прошли обучение.

---

## 📊 1. ПОКАЗАТЬ ДАННЫЕ КЛИЕНТОВ

### Статистика через API:

```bash
# Клиент 1
curl http://localhost:8000/api/v1/stats | python -m json.tool

# Клиент 2
curl http://localhost:8001/api/v1/stats | python -m json.tool
```

### Или через Swagger UI:
- **Клиент 1**: http://localhost:8000/docs
- **Клиент 2**: http://localhost:8001/docs

---

## 🚀 2. ЗАПУСТИТЬ ДООБУЧЕНИЕ

### Запуск обучения на клиентах:

```bash
# Запустить обучение на клиенте 1
curl -X POST http://localhost:8000/api/v1/train | python -m json.tool

# Запустить обучение на клиенте 2
curl -X POST http://localhost:8001/api/v1/train | python -m json.tool
```

**Ожидаемый ответ:**
```json
{
  "status": "training_started",
  "message": "Federated learning training cycle started in background"
}
```

---

## 📺 3. МОНИТОРИНГ ОБУЧЕНИЯ

### Логи в реальном времени:

```bash
# Все клиенты + сервер
docker-compose logs -f fl-client-1 fl-client-2 fl-server

# Только клиент 1
docker-compose logs -f fl-client-1

# Только клиент 2
docker-compose logs -f fl-client-2

# Только сервер
docker-compose logs -f fl-server
```

### Что искать в логах клиентов:

```
[OK] УСПЕШНОЕ ОБУЧЕНИЕ:
✓ Downloaded global weights from server
✓ Loaded X training samples from Y files
Epoch 1/3, Loss: X.XX
Epoch 2/3, Loss: X.XX
Epoch 3/3, Loss: X.XX
✓ Training completed on X examples
✓ Delta uploaded successfully
✓ Model hot reloaded successfully
```

---

## 🔍 4. ПОСМОТРЕТЬ ДЕЛЬТЫ

### Список дельт в MinIO:

```bash
python -c "
from minio import Minio
client = Minio('localhost:9000', access_key='admin', secret_key='admin12345', secure=False)
objects = list(client.list_objects('mybucket', prefix='weights/clients/', recursive=True))
print(f'Total deltas: {len(objects)}\n')
for obj in objects:
    parts = obj.object_name.split('_')
    client_id = parts[1][-4:] if len(parts) > 1 else 'unknown'
    num_examples = parts[2] if len(parts) > 2 else '?'
    print(f'Client {client_id}: {num_examples} examples, {obj.size/1024:.2f} KB, uploaded: {obj.last_modified}')
"
```

### Через MinIO Console (визуально):

1. Откройте: http://localhost:9001
2. Войдите: `admin` / `admin12345`
3. Перейдите: **`mybucket`** → **`weights/`** → **`clients/`**

Вы увидите файлы типа:
```
20260118T221824Z_550e8400-...-440001_18_5a1395bb-...-37dd1.pt
└─ timestamp   └─ client_id     └─ examples └─ run_id
```

---

## 🎯 5. ПОСМОТРЕТЬ ЧТО ДЕЛАЕТ СЕРВЕР

### Проверить что сервер работает:

```bash
# Логи сервера
docker-compose logs --tail=50 fl-server

# Ищите строки:
# [INFO] starting aggregation  <- Каждую минуту (проверка)
# [INFO] gRPC server listening at [::]:8081  <- Запущен
```

**ВАЖНО**: Логи показывают только `starting aggregation`, но **реальная агрегация происходит каждые 10 минут**, когда есть новые дельты!

### Проверить что агрегация реально работает:

```bash
# Автоматическая диагностика (рекомендуется)
python scripts/diagnose-fl-system.py

# Или проверьте время обновления глобальной модели:
python -c "
from minio import Minio
client = Minio('localhost:9000', access_key='admin', secret_key='admin12345', secure=False)
stat = client.stat_object('mybucket', 'weights/global/latest.pt')
print(f'Глобальная модель обновлена: {stat.last_modified}')

# Сравните со временем загрузки дельт
deltas = list(client.list_objects('mybucket', prefix='weights/clients/', recursive=True))
if deltas:
    latest_delta = max(deltas, key=lambda x: x.last_modified)
    print(f'Последняя дельта загружена: {latest_delta.last_modified}')
    if stat.last_modified > latest_delta.last_modified:
        print('[OK] Модель обновлена ПОСЛЕ загрузки дельт - агрегация работает!')
    else:
        print('[WAIT] Ожидайте агрегацию (происходит каждые 10 минут)')
"
```

### Проверить записи в PostgreSQL:

```bash
docker exec fl-postgres psql -U fluser -d fl_metadata -c "SELECT client_id, num_examples, created_at FROM weights ORDER BY created_at DESC LIMIT 10;"
```

Вы увидите:
```
client_id                             | num_examples | created_at
--------------------------------------+--------------+-------------------
550e8400-e29b-41d4-a716-446655440002 |           20 | 2026-01-18 22:18:56
550e8400-e29b-41d4-a716-446655440001 |           18 | 2026-01-18 22:18:24
```

---

## 🌐 6. ФРОНТЕНДЫ

### Откройте в браузере:

- **Пользователь 1**: `apps/frontend/demo1/index.html`
- **Пользователь 2**: `apps/frontend/demo2/index.html`

### Как сделать свайп:

1. Наведите курсор на первую букву
2. Нажмите и удерживайте левую кнопку мыши
3. Проведите курсором по всем буквам слова (не отпуская!)
4. Отпустите кнопку мыши на последней букве
5. Нажмите "Предсказать слово"
6. Если неправильно - исправьте и нажмите "Сохранить исправленное"
7. Если правильно - нажмите "Принять"

---

## 📈 7. ПОЛНЫЙ ЦИКЛ ДЕМОНСТРАЦИИ

### Шаг 1: Проверка начального состояния

```bash
docker-compose ps
curl http://localhost:8000/api/v1/stats | python -m json.tool
curl http://localhost:8001/api/v1/stats | python -m json.tool
```

### Шаг 2: Сбор данных (через фронтенд)

- Откройте `demo1/index.html` - сделайте 3-5 свайпов
- Откройте `demo2/index.html` - сделайте 3-5 свайпов

### Шаг 3: Проверка что данные сохранились

```bash
curl http://localhost:8000/api/v1/stats | python -m json.tool
curl http://localhost:8001/api/v1/stats | python -m json.tool
```

### Шаг 4: Запуск обучения

```bash
# В отдельном терминале откройте логи:
docker-compose logs -f fl-client-1 fl-client-2 fl-server

# В другом терминале запустите обучение:
curl -X POST http://localhost:8000/api/v1/train
sleep 5
curl -X POST http://localhost:8001/api/v1/train
```

### Шаг 5: Наблюдение за процессом

В логах вы увидите:
1. Клиенты скачивают глобальную модель
2. Обучаются на своих данных
3. Вычисляют дельты
4. Загружают дельты на сервер
5. Модели обновляются

### Шаг 6: Проверка результата

```bash
# Проверьте дельты в MinIO:
python -c "
from minio import Minio
client = Minio('localhost:9000', access_key='admin', secret_key='admin12345', secure=False)
objects = list(client.list_objects('mybucket', prefix='weights/clients/', recursive=True))
print(f'Deltas uploaded: {len(objects)}')
"

# Проверьте записи в PostgreSQL:
docker exec fl-postgres psql -U fluser -d fl_metadata -c "SELECT COUNT(*) FROM weights;"
```

---

## 🎓 Ключевые моменты для демонстрации

### ✅ Подчеркните:

1. **Privacy by Design**
   - Данные клиента 1: 18 свайпов (только локально)
   - Данные клиента 2: 20 свайпов (только локально)
   - Сервер получил только **дельты** (изменения весов), не данные!

2. **Децентрализованное обучение**
   - Каждый клиент обучается независимо
   - Данные не покидают устройства
   - Легко масштабировать (добавить больше клиентов)

3. **Агрегация на сервере**
   - Сервер собирает дельты от всех клиентов
   - Выполняет FedAvg (взвешенное усреднение)
   - Создает улучшенную глобальную модель

4. **Production-ready архитектура**
   - Docker контейнеры (изоляция)
   - gRPC коммуникация (эффективная)
   - MinIO для хранения моделей
   - PostgreSQL для метаданных
   - Background tasks (асинхронность)
   - Hot reload моделей (без перезапуска)

---

## ⚠️ Troubleshooting

### Если обучение не запускается:

```bash
# Проверьте что модель в MinIO:
python -c "
from minio import Minio
client = Minio('localhost:9000', access_key='admin', secret_key='admin12345', secure=False)
try:
    stat = client.stat_object('mybucket', 'weights/global/latest.pt')
    print(f'[OK] Model found: {stat.size/1024/1024:.2f} MB')
except:
    print('[ERROR] Model not found!')
"

# Если не найдена, загрузите:
python -c "
from minio import Minio
from pathlib import Path
client = Minio('localhost:9000', access_key='admin', secret_key='admin12345', secure=False)
client.fput_object('mybucket', 'weights/global/latest.pt', 'apps/server/models/initial_model.pt')
print('[OK] Model uploaded')
"
```

### Если контейнеры упали:

```bash
docker-compose down
docker-compose up -d
```

### Если нужно очистить данные:

```bash
docker-compose down -v  # ВНИМАНИЕ: удалит все данные!
docker-compose up -d
# Затем загрузите модель снова
```

---

## 🎬 Время демонстрации: 15-20 минут

**Готово к показу!** 🚀

