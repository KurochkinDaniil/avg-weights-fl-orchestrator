# Federated Learning Swipe Keyboard

Клавиатура со свайп-жестами + распределённое обучение модели.

---

### Клонировать и запустить:

```bash
git clone https://github.com/KurochkinDaniil/avg-weights-fl-orchestrator.git
cd avg-weights-fl-orchestrator
make dev  # или make up для полной системы
```

### Открыть:

```
http://localhost:3000/demo/index.html
```

**Примечание:** `make dev` и `make up` автоматически инициализируют git submodules.

---

## Команды

```bash
make dev       # Запустить только клиент + frontend (без сервера)
make up        # Запустить полную систему (с PostgreSQL, MinIO, Go-сервером)
make down      # Остановить все контейнеры
make logs      # Показать логи
make status    # Показать статус
make train     # Запустить обучение
make clean     # Удалить всё
```