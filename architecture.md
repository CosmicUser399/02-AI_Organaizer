# Архитектура проекта "AI-Органайзер"

Документ фиксирует стек технологий и архитектуру приложения перед
началом реализации. Источник требований: [spec.md](spec.md).

## Ключевые решения

- Реализуется **весь функционал спецификации**: Magic Input,
  AI-декомпозиция задач, AI-заметки с семантическим поиском,
  адаптивный планировщик, вечерний AI-дайджест.
- Режим работы: **однопользовательский, локальный**, без
  регистрации и логина.
- Архитектура: отдельные **backend** (FastAPI) и **frontend**
  (React + MUI, Vite), взаимодействующие по REST API.
- **Контейнеризация**: Docker + Docker Compose для изоляции
  окружения и упрощения развёртывания (опционально, доступен
  также локальный запуск без Docker).

## Стек технологий

### Backend

- **Python 3** — язык реализации.
- **FastAPI** — REST API, асинхронность, автогенерация OpenAPI.
- **SQLAlchemy** — ORM поверх **SQLite** (файл БД).
- **Pydantic / pydantic-settings** — схемы запросов/ответов и
  конфигурация из `.env`.
- **OpenAI Python SDK** — интеграция с моделями:
  - `OPENAI_CHAT_MODEL` (`gpt-4o-mini`) — парсинг, декомпозиция,
    автотеги, форматирование текста, reschedule, дайджест;
  - `EMBEDDING_MODEL` (`text-embedding-3-small`) — эмбеддинги для
    семантического поиска по заметкам.
- **uvicorn** — ASGI-сервер.
- **logging** (стандартная библиотека) — вместо `print`.
- **ruff / black / isort** — линтер и форматтер, `line-length = 79`
  под принятые стайл-правила.

### Frontend

- **Node.js + npm** — окружение и пакетный менеджер.
- **React** — UI-библиотека.
- **Material UI (MUI)** — компоненты интерфейса (кнопки, списки,
  диалоги, чипы тегов).
- **Vite** — сборка и dev-сервер (`npm run dev/build/preview`).
- **ESLint + Prettier** — линтер и форматтер JS/JSX.
- **localStorage** — хранение истории последних введённых строк
  Magic Input на клиенте (не основное хранилище данных).

### Хранение данных

- **SQLite** — единственный источник истины для задач, чек-листов
  и заметок (файл `backend/data/app.db`).
- Векторный поиск не выносится во внешнюю БД: эмбеддинги хранятся
  как JSON-поле в SQLite, косинусная близость считается в Python
  (достаточно для локального однопользовательского масштаба).

### Контейнеризация (Docker)

- **Docker** — для изоляции окружения и воспроизводимых сборок.
- **Docker Compose** — оркестрация backend и frontend контейнеров.
- **Два режима**:
  - `docker-compose.yml` — development с hot-reload и volume
    mount для исходников.
  - `docker-compose.prod.yml` — production с nginx для frontend
    и оптимизированными образами.
- **Multi-stage builds** — frontend собирается через промежуточный
  образ builder, итоговый production образ содержит только
  статику + nginx (легковесный).

## Архитектурная диаграмма

```mermaid
flowchart LR
    subgraph frontend [Frontend: React + MUI + Vite]
        MagicInput
        TaskList
        NotesPanel
        Planner
        DigestCard
    end

    subgraph backend [Backend: FastAPI]
        TasksAPI["/tasks"]
        NotesAPI["/notes"]
        ScheduleAPI["/schedule"]
        InsightsAPI["/insights"]
        AIService["AI Service Layer"]
    end

    DB[("SQLite\ntasks, checklist_items,\nnotes, note_chunks")]
    OpenAI[("OpenAI API\nChat + Embeddings")]

    frontend -->|"fetch /api/*\n(Vite dev proxy)"| backend
    TasksAPI --> DB
    NotesAPI --> DB
    ScheduleAPI --> DB
    InsightsAPI --> DB
    AIService --> OpenAI
    TasksAPI --> AIService
    NotesAPI --> AIService
    ScheduleAPI --> AIService
    InsightsAPI --> AIService
```

В dev-режиме через Docker фронтенд обращается к бэкенду через прокси
Vite (`/api -> http://backend:18080`). Имя `backend` доступно только
внутри Docker-сети; браузер обращается к frontend на
`http://localhost:5173`. CORS middleware на бэкенде всё равно
включается для устойчивости при других сценариях запуска.

Роутер задач FastAPI объявлен с завершающим `/`. Поэтому frontend
должен использовать `/api/tasks/` для коллекции задач (GET, POST и
DELETE all). Запрос без завершающего `/` получает HTTP 307 и может
перенаправить браузер на внутренний адрес `backend:18080`, который
недоступен с хост-машины.

## Структура проекта

```
02-AI_Organaizer/
  spec.md
  architecture.md
  .env                  # существующий, с секретами (в .gitignore)
  .env.example          # шаблон без секретов
  .gitignore
  README.md
  docker-compose.yml         # Docker Compose для development
  docker-compose.prod.yml    # Docker Compose для production
  backend/
    app/
      main.py            # FastAPI app, CORS, роутеры, логирование
      config.py           # pydantic-settings, читает .env
      database.py          # SQLAlchemy engine/session
      models.py             # Task, ChecklistItem, Note, NoteChunk
      schemas.py             # Pydantic-схемы запросов/ответов
      routers/
        tasks.py
        notes.py
        schedule.py
        insights.py
      services/
        openai_client.py     # обёртка над OpenAI SDK
        capture.py            # парсинг Magic Input -> задача
        decompose.py           # разбивка задачи на шаги/подсказки
        notes_ai.py             # автотеги, связи, форматирование
        embeddings.py            # embeddings, cosine similarity
        scheduler.py              # приоритеты (Эйзенхауэр), reschedule
        digest.py                  # вечерний дайджест
    requirements.txt
    pyproject.toml         # ruff/black/isort (line-length=79)
    Dockerfile             # образ для backend
    .dockerignore
  frontend/
    src/
      main.jsx
      App.jsx
      theme.js
      api/client.js         # fetch-обёртка, baseURL через Vite proxy
      components/
        MagicInput.jsx
        TaskList.jsx / TaskItem.jsx
        ChecklistDialog.jsx
        NotesPanel.jsx / NoteEditor.jsx / AskNotesBar.jsx
        Planner.jsx           # матрица Эйзенхауэра / фокус на день
        DigestCard.jsx
    vite.config.js         # dev-proxy /api -> backend:18080
    package.json
    eslint.config.js / .prettierrc
    Dockerfile             # multi-stage образ для frontend
    .dockerignore
    nginx.conf             # конфигурация nginx для production
```

## Модель данных (SQLite)

| Сущность | Поля |
| --- | --- |
| **Task** | `id, title, raw_input, description, due_at, tag, is_urgent, is_important, status(pending/in_progress/done), created_at, updated_at` |
| **ChecklistItem** | `id, task_id (FK), text, is_done, position, created_at` |
| **Note** | `id, title, content, tags(JSON), linked_task_id (FK, nullable), created_at, updated_at` |
| **NoteChunk** | `id, note_id (FK), text, embedding(JSON[float])` |

Заметка режется на абзацы; каждый абзац (`NoteChunk`) получает свой
embedding, чтобы семантический поиск находил конкретный релевантный
фрагмент, а не всю заметку целиком.

## Точки интеграции с OpenAI

1. **Magic Input** — парсинг свободного текста в структурированную
   задачу (`title`, `due_at`, `tag`).
2. **Декомпозиция задач** — генерация чек-листа шагов и
   контекстных подсказок по недостающим подзадачам.
3. **Автотегирование заметок** — теги и предложение связей с
   задачами/проектами при создании/редактировании заметки.
4. **Семантический поиск** — эмбеддинги вопроса и абзацев заметок,
   выдача релевантных фрагментов ("Спроси свои заметки").
5. **Быстрое форматирование** — summary / исправление грамматики /
   смена тона для выделенного фрагмента заметки.
6. **Smart Rescheduling** — анализ загруженности дня и предложение
   нового окна для просроченной задачи.
7. **Вечерний дайджест** — агрегация статистики дня (% выполнения,
   продуктивные часы) и генерация текстового отчёта-рекомендации.

## API (обзор эндпоинтов)

- `GET/POST/PATCH/DELETE /tasks`, `DELETE /tasks` (очистить список)
- `POST /tasks/parse` — Magic Input -> черновик задачи
- `POST /tasks/{id}/decompose` — генерация чек-листа
- `POST /tasks/{id}/reschedule` — предложение нового времени
- `GET/POST/PATCH/DELETE /notes`
- `POST /notes/ask` — семантический поиск по заметкам
- `POST /notes/{id}/transform` — summary/грамматика/тон
- `GET /schedule/today` — приоритеты дня (матрица Эйзенхауэра)
- `GET /insights/digest` — вечерний AI-дайджест

## Примечания

- `.env` уже содержит боевой ключ OpenAI — обязательно должен быть
  добавлен в `.gitignore`; в репозиторий попадает только
  `.env.example` без секретов.
- Настоящий документ фиксирует архитектуру на момент планирования;
  при изменении решений в ходе реализации файл следует обновлять.
