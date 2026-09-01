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

### Вариант 1: Запуск через Docker (рекомендуется)

> 📘 Полная документация по Docker: [DOCKER.md](DOCKER.md)

#### Предварительные требования

- Docker и Docker Compose
- OpenAI API ключ

#### Настройка и запуск

1. Создайте файл `.env` в корне проекта:

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
API_BASE_URL=http://localhost:18080
```

2. Запустите приложение:

```bash
# Development режим (с hot-reload)
docker-compose up

# Production режим
docker-compose -f docker-compose.prod.yml up -d

# Остановка
docker-compose down

# Пересборка после изменений
docker-compose up --build
```

**Приложение будет доступно:**
- Frontend (dev): http://localhost:5173
- Frontend (prod): http://localhost:80
- Backend API: http://localhost:18080
- API документация: http://localhost:18080/docs

В Docker development-режиме frontend использует Vite-прокси
`/api -> http://backend:18080`. В браузере используются только
относительные API-адреса `/api/...`; имя `backend` доступно только
внутри Docker-сети. Для списка задач используйте завершающий `/`:
`/api/tasks/`. Это предотвращает перенаправление HTTP 307 на
недоступный браузеру внутренний адрес.

---

### Вариант 2: Локальный запуск (без Docker)

#### Предварительные требования

- Python 3.11 или выше
- Node.js 18 или выше
- OpenAI API ключ

#### 1. Настройка окружения

Создайте файл `.env` в корне проекта (используйте `.env.example` как шаблон):

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
API_BASE_URL=http://localhost:18080
```

#### 2. Запуск Backend

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

#### 3. Запуск Frontend

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

#### 4. Production сборка (локально)

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
│   ├── pyproject.toml
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/             # Frontend приложение
│   ├── src/
│   │   ├── main.jsx      # Точка входа
│   │   ├── App.jsx       # Главный компонент
│   │   ├── theme.js      # MUI тема
│   │   ├── api/          # API клиент
│   │   └── components/   # React компоненты
│   ├── vite.config.js
│   ├── package.json
│   ├── Dockerfile
│   ├── .dockerignore
│   └── nginx.conf
├── docker-compose.yml       # Docker Compose для dev
├── docker-compose.prod.yml  # Docker Compose для prod
├── .env                     # Секреты (не в git)
├── .env.example             # Шаблон переменных
├── .gitignore
├── spec.md                  # Спецификация
├── architecture.md          # Архитектура
├── DOCKER.md                # Docker документация
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

### Docker команды

```bash
# Запуск в development режиме
docker-compose up

# Запуск в background
docker-compose up -d

# Остановка
docker-compose down

# Остановка с удалением volumes (БД)
docker-compose down -v

# Пересборка образов
docker-compose build

# Просмотр логов
docker-compose logs -f

# Запуск production версии
docker-compose -f docker-compose.prod.yml up -d

# Выполнение команды в контейнере backend
docker-compose exec backend python -m app.some_script

# Выполнение команды в контейнере frontend
docker-compose exec frontend npm run lint
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

## Docker файлы

Проект включает полную поддержку Docker для удобного развёртывания:

- `backend/Dockerfile` - образ для Python/FastAPI приложения
- `frontend/Dockerfile` - multi-stage образ (development + production с nginx)
- `docker-compose.yml` - оркестрация для development с hot-reload
- `docker-compose.prod.yml` - оркестрация для production
- `frontend/nginx.conf` - конфигурация nginx для production
- `DOCKER.md` - подробная документация по использованию Docker

Подробные инструкции см. в [DOCKER.md](DOCKER.md).

## Лицензия

Проект создан для образовательных целей.

## Автор

AI-Органайзер - проект курса по разработке AI-приложений.
