# Federated Learning Swipe Keyboard

Клавиатура со свайп-жестами + локальное обучение модели.

## Быстрый старт

**С Git Bash (Windows/Mac/Linux):**
```bash
./start.sh
```

**Или вручную (Windows CMD/PowerShell):**
```bash
# Terminal 1 - Backend
cd apps\client
venv\Scripts\activate
python scripts\run_api.py

# Terminal 2 - Frontend  
cd apps\frontend
start demo\index.html
```

Откроется браузер с клавиатурой:
1. Делаешь свайп по буквам
2. Нажимаешь "Предсказать слово"
3. Видишь предсказание - можешь:
   - **✓ Принять** - если правильно
   - **✓ Сохранить исправленное** - если неправильно (исправь в поле)
   - **✗ Отменить** - если не нужно

Только подтверждённые слова сохраняются для обучения!

## Что запускается

- **Backend API** на `http://localhost:8000` (FastAPI, PyTorch)
- **Frontend** в браузере (клавиатура)

## Проверить

```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

## Обучение (Windows/Linux)

После того как собрали 20+ свайпов:

```bash
cd apps/client
./train.sh
```

Подождать 5-30 минут. Модель обучится на ваших данных.

**Для Mac:** Inference и сбор данных работают. Обучение запускать на Windows/Linux.

## Остановить

```bash
# Найти процесс
lsof -ti:8000

# Убить
lsof -ti:8000 | xargs kill -9
```

## Структура

```
fl/
├── start.sh              # Запуск всего
├── apps/
│   ├── frontend/         # Клавиатура (JS)
│   ├── client/           # Backend (Python)
│   │   ├── run.sh       # Только API
│   │   └── train.sh     # Обучение
│   └── server/          # Go сервер (не используется пока)
```

## Настройки

Ускорить обучение:

```bash
# apps/client/.env
NUM_EPOCHS=2
BATCH_SIZE=64
```

