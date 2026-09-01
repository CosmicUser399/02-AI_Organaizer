# AI-Органайзер

Умный планировщик задач с искусственным интеллектом, который помогает управлять делами, заметками и временем.

## Возможности

- **Magic Input**: естественный язык для создания задач с автоматическим парсингом дат и приоритетов
- **AI-декомпозиция**: автоматическая разбивка сложных задач на конкретные шаги
- **Умные заметки**: автоматическая генерация тегов и поиск связанных задач
- **Семантический поиск**: поиск по заметкам на основе смысла вопроса
- **Адаптивный планировщик**: матрица Эйзенхауэра и умный перенос просроченных задач
- **Вечерний дайджест**: AI-анализ продуктивности и планирование завтрашнего дня

## Стек технологий

### Backend
- Python 3.11+
- FastAPI (веб-фреймворк)
- SQLAlchemy + SQLite (база данных)
- OpenAI API (Chat + Embeddings)
- Pydantic (валидация данных)

### Frontend
- React 18
- Vite (сборщик)
- Material UI (компоненты)
- Fetch API (работа с backend)

## Установка и запуск

### Предварительные требования

- Python 3.11 или выше
- Node.js 18 или выше
- OpenAI API ключ

### 1. Настройка окружения

Создайте файл `.env` в корне проекта (используйте `.env.example` как шаблон):

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
API_BASE_URL=http://localhost:18080
```

### 2. Запуск Backend

```bash
# Перейдите в директорию backend
cd backend

# Создайте виртуальное окружение
python -m venv .venv

# Активируйте виртуальное окружение
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Запустите сервер
uvicorn app.main:app --reload --port 18080
```

Backend будет доступен по адресу: http://localhost:18080

Документация API (Swagger): http://localhost:18080/docs

### 3. Запуск Frontend

Откройте новый терминал:

```bash
# Перейдите в директорию frontend
cd frontend

# Установите зависимости
npm install

# Запустите dev-сервер
npm run dev
```

Frontend будет доступен по адресу: http://localhost:5173

### 4. Production сборка

```bash
# Backend: используйте production ASGI сервер
uvicorn app.main:app --host 0.0.0.0 --port 18080

# Frontend: соберите статику
cd frontend
npm run build
npm run preview
```

## Структура проекта

```
02-AI_Organaizer/
├── backend/              # Backend приложение
│   ├── app/
│   │   ├── main.py       # FastAPI приложение
│   │   ├── config.py     # Конфигурация
│   │   ├── database.py   # База данных
│   │   ├── models.py     # SQLAlchemy модели
│   │   ├── schemas.py    # Pydantic схемы
│   │   ├── routers/      # API endpoints
│   │   └── services/     # Бизнес-логика и AI
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/             # Frontend приложение
│   ├── src/
│   │   ├── main.jsx      # Точка входа
│   │   ├── App.jsx       # Главный компонент
│   │   ├── theme.js      # MUI тема
│   │   ├── api/          # API клиент
│   │   └── components/   # React компоненты
│   ├── vite.config.js
│   └── package.json
├── .env                  # Секреты (не в git)
├── .env.example          # Шаблон переменных
├── .gitignore
├── spec.md               # Спецификация
├── architecture.md       # Архитектура
└── README.md
```

## Разработка

### Code Style

**Python:**
- Отступы: 4 пробела
- Длина строки: ≤79 символов
- Форматирование: `black`, `isort`, `ruff`
- Type hints обязательны
- Докстринги в формате PEP 257

**JavaScript/React:**
- Отступы: 2 пробела
- ESLint + Prettier
- Функциональные компоненты + хуки
- Нет `console.log` в production коде

### Линтинг и форматирование

```bash
# Backend
cd backend
ruff check .
black --check .
isort --check-only .

# Frontend
cd frontend
npm run lint
npm run format
```

## API Endpoints

- `GET /` - информация о приложении
- `GET /health` - проверка работоспособности
- `POST /tasks` - создать задачу
- `GET /tasks` - получить список задач
- `PATCH /tasks/{id}` - обновить задачу
- `DELETE /tasks/{id}` - удалить задачу

*(полный список endpoints будет дополнен по мере разработки)*

## База данных

SQLite база данных создается автоматически при первом запуске backend.

Модели:
- `Task` - задачи
- `ChecklistItem` - пункты чек-листов
- `Note` - заметки
- `NoteChunk` - фрагменты заметок с embeddings

## Лицензия

Проект создан для образовательных целей.

## Автор

AI-Органайзер - проект курса по разработке AI-приложений.
