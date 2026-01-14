# Federated Learning Swipe Keyboard

Клавиатура со свайп-жестами + распределённое обучение модели.

---

### 1Клонировать с submodules:

```bash
git clone --recurse-submodules https://github.com/KurochkinDaniil/avg-weights-fl-orchestrator.git
cd fl
```

### Запустить:

**Только клавиатура + inference (без сервера):**
```bash
make dev
```

**Полная система (с FL-сервером):**
```bash
make up
```

### Открыть в браузере:

```
http://localhost:3000/demo/index.html
```

---

## Команды Makefile

```bash
make dev       # Запустить только клиент + frontend (без сервера)
make up        # Запустить полную систему (с PostgreSQL, MinIO, Go-сервером)
make down      # Остановить все контейнеры
make logs      # Показать логи всех сервисов
make build     # Пересобрать Docker образы
make clean     # Удалить все контейнеры и volumes
make train     # Войти в контейнер и запустить обучение
make status    # Показать статус контейнеров
```