# AI-Органайзер

Локальный однопользовательский планировщик задач с искусственным
интеллектом: умный ввод, чек-листы, заметки, приоритеты на день и
вечерний дайджест.

## Возможности

- **Magic Input** — задача из свободной фразы на русском языке; ИИ 
  извлекает заголовок, дату, тег и приоритет. Если разбор не удался, 
  задача всё равно создаётся как есть.
- **Редактирование задач** — полноценное редактирование заголовка,
  описания, даты/времени выполнения, категории и приоритетов через
  диалоговое окно.
- **AI-декомпозиция** — кнопка «Разбить на шаги» строит чек-лист и
  подсказки на русском языке; шаги можно добавлять, редактировать
  (inline-режим) и удалять.
- **Умные заметки** — автотеги на русском языке и предложение связи
  с существующими задачами.
- **Семантический поиск** — «Спроси свои заметки»: поиск по смыслу и
  краткий AI-ответ на русском по найденным фрагментам.
- **Быстрое форматирование** — выделение текста в заметке: краткое
  резюме, грамматика, деловой или дружелюбный тон (на русском языке).
- **Адаптивный планировщик** — матрица Эйзенхауэра, фокус дня и
  предложение нового окна для просроченных задач (на русском языке).
- **Вечерний дайджест** — отчёт о продуктивности на русском языке
  с учётом прогресса по подзадачам; кэш на календарный день 
  (`?refresh=true` пересобирает).

История последних строк Magic Input хранится в `localStorage`.
Задачи, чек-листы и заметки живут в SQLite, не в браузере.

**Важно:** Все AI-генерируемые тексты (формулировки задач, шаги
выполнения, подсказки, теги, дайджесты) создаются на русском языке.

## Стек технологий

### Backend

- Python 3.11+
- FastAPI, uvicorn
- SQLAlchemy + SQLite
- Pydantic / pydantic-settings
- OpenAI API (Chat + Embeddings)
- ruff, black, isort (`line-length = 79`)

Для совместимости OpenAI SDK зафиксирована пара
`openai==1.47.0` и `httpx==0.27.2`. Не обновляйте их по отдельности
без проверки запуска backend.

### Frontend

- React 18, Vite
- Material UI v6 — кастомная тема «Deep Space»: тёмный режим
  (`mode: 'dark'`), electric blue (`#60a5fa`) / neon cyan (`#22d3ee`),
  glassmorphism-карточки, gradient-кнопки с glow, Inter 400/600/700
  через `@fontsource/inter`
- ESLint + Prettier
- все HTTP-запросы только через `src/api/client.js`
- общие утилиты форматирования — `src/utils.js`

## Переменные окружения

Скопируйте `.env.example` в `.env` в корне проекта:

| Переменная | Назначение | Пример |
| --- | --- | --- |
| `OPENAI_API_KEY` | Ключ OpenAI | `sk-...` |
| `OPENAI_CHAT_MODEL` | Чат-модель | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Эмбеддинги для поиска | `text-embedding-3-small` |
| `API_BASE_URL` | URL API (справка / клиенты) | `http://localhost:18080` |

Файл `.env` не коммитится. Без валидного ключа AI-функции вернут
понятную ошибку (таймаут, сеть, лимит, неверный ключ).

## Установка и запуск

### Вариант 1: Docker (рекомендуется)

Полная документация: [DOCKER.md](DOCKER.md).

```bash
# Development (hot-reload)
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up -d
```

Доступ:

- Frontend (dev): http://localhost:5173
- Frontend (prod): http://localhost:80
- Backend API: http://localhost:18080
- OpenAPI: http://localhost:18080/docs

В Docker frontend проксирует `/api` на `http://backend:18080`.
В браузере используйте относительные адреса `/api/...`. Для списка
задач нужен завершающий слэш: `/api/tasks/`.

### Вариант 2: Локально, без Docker

Нужны Python 3.11+ и Node.js 18+.

**Backend:**

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 18080
```

**Frontend** (второй терминал):

```bash
cd frontend
npm install
npm run dev
```

- Dev: http://localhost:5173 (`npm run dev`)
- Сборка: `npm run build`
- Проверка сборки: `npm run preview`

Локальный Vite по умолчанию проксирует `/api` на Docker-имя
`backend`. Если backend запущен на хосте, используйте Docker для
обоих сервисов или поправьте `proxy.target` в `vite.config.js` на
`http://localhost:18080`.

## Структура проекта

```
02-AI_Organaizer/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── exceptions.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   └── services/
│   │       ├── capture.py         # русификация промптов
│   │       ├── decompose.py       # русификация промптов
│   │       ├── notes_ai.py        # русификация промптов
│   │       └── scheduler.py       # русификация промптов
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.js
│   │   ├── theme.js
│   │   ├── utils.js
│   │   └── components/
│   │       ├── EditTaskDialog.jsx     # новый компонент
│   │       ├── TaskItem.jsx           # кнопка редактирования
│   │       └── ChecklistDialog.jsx    # inline-редактирование
│   ├── vite.config.js
│   └── package.json
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── spec.md
├── architecture.md
├── DOCKER.md
├── CHANGELOG.md
└── README.md
```

## Разработка

### Стиль кода

**Python:** 4 пробела, длина строки ≤79, type hints, PEP 257,
`logging` вместо `print`.

**JavaScript/React:** функциональные компоненты и хуки, Prettier
(2 пробела), без `console.log` в итоговом коде.

### Линтинг и форматирование

```bash
# Backend (из backend/, с активированным venv)
ruff check .
black --check .
isort --check-only .
# автоисправление:
ruff check --fix .
black .
isort .

# Frontend (из frontend/)
npm run lint
npm run format:check
npm run format
```

## API

- `GET /health` — проверка работоспособности
- `GET/POST /tasks/`, `PATCH/DELETE /tasks/{id}`
- `DELETE /tasks/` — очистить список
- `POST /tasks/parse` — Magic Input
- `POST /tasks/{id}/decompose` — чек-лист через AI
- `GET/POST /tasks/{id}/checklist`, `PATCH/DELETE .../checklist/{item_id}`
- `POST /tasks/{id}/reschedule` — предложение нового времени
- `GET/POST /notes/`, `PATCH/DELETE /notes/{id}`
- `POST /notes/ask` — семантический поиск
- `POST /notes/{id}/transform` — форматирование выделения
- `GET /notes/{id}/suggested-tasks` — связанные задачи
- `GET /schedule/today` — фокус дня и матрица Эйзенхауэра
- `GET /insights/digest` — вечерний дайджест (`?date=`, `?refresh=true`)

Коллекционные URL: `/api/tasks/` и `/api/notes/` (завершающий `/`).

Вызовы OpenAI на backend ограничены таймаутом ~40 с (одна повторная
попытка). Frontend ждёт до 90 с и показывает ошибку сети, таймаута
или OpenAI без сырого стека. На экранах загрузки есть лоадеры, пустые
списки и кнопка «Повторить».

### Сохранение заметок

Создание и редактирование заметки сначала сохраняются в SQLite и
сразу возвращают ответ frontend. Автотеги и переиндексация embeddings
выполняются в фоновой задаче, поэтому задержки OpenAI не блокируют
кнопку сохранения. Если AI-сервис временно недоступен, сама заметка
остаётся сохранённой, а ошибка фоновой обработки записывается в лог
backend.

При формировании дайджеста статистика сначала считывается из SQLite,
после чего соединение с базой закрывается перед вызовом OpenAI. Это
предотвращает удержание read-lock и блокировку параллельного
сохранения заметок.

## Использование новых возможностей

### Редактирование задач

Каждая задача имеет кнопку **редактирования (✏️)** рядом с кнопками
декомпозиции и удаления:

1. Нажмите на иконку ✏️ для открытия диалога редактирования
2. Измените любые поля:
   - Заголовок задачи
   - Описание
   - Дату и время выполнения
   - Категорию (работа, личное, здоровье и т.д.)
   - Флаги "Срочная" и "Важная"
3. Нажмите "Сохранить" для применения изменений

### Редактирование шагов чек-листа

В диалоге декомпозиции задачи доступно inline-редактирование шагов:

1. Откройте чек-лист задачи (иконка ✨ "Разбить на шаги")
2. Нажмите на иконку **✏️** рядом с нужным шагом
3. Отредактируйте текст прямо в появившемся поле
4. **Сохраните изменения:**
   - Нажмите ✓ (галочка) или клавишу `Enter`
5. **Отмените редактирование:**
   - Нажмите ✕ (крестик) или клавишу `Escape`

Вы также можете:
- Добавлять новые шаги вручную
- Удалять шаги (иконка 🗑️)
- Отмечать шаги как выполненные

### Русский язык AI

Все AI-генерируемые тексты создаются на русском языке:
- Формулировки задач при парсинге Magic Input
- Шаги выполнения и подсказки при декомпозиции
- Теги и резюме заметок
- Предложения по переносу просроченных задач
- Вечерний дайджест продуктивности

## Устранение типовых проблем

### Backend: HTTP 500 или не стартует

```bash
docker-compose logs --since 5m backend
```

Если в логах `unexpected keyword argument 'proxies'`:

```bash
docker-compose build --no-cache backend
docker-compose up -d backend
```

### Frontend: ERR_CONNECTION_RESET или пустой экран

Проверьте HMR в `frontend/vite.config.js`: `hmr.clientPort: 5173`,
`hmr.host: 'localhost'`, `watch.usePolling: true`. Затем:

```bash
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### `validateDOMNesting` в консоли

Если передаёте JSX в `ListItemText.secondary`, используйте
`component="span"` на всех вложенных элементах (MUI оборачивает
`secondary` в `<p>`, блочные элементы внутри него вызывают ошибку).
Пример правильного использования — `TaskItem.jsx`.

## База данных

SQLite создаётся при старте backend: `backend/data/ai_organizer.db`
(в Docker эта папка — volume).

Модели: `Task`, `ChecklistItem`, `Note`, `NoteChunk`.

### Резервное копирование

```bash
# Windows
backup_db.bat

# Linux/macOS
chmod +x backup_db.sh
./backup_db.sh

# или
python backup_db.py
```

Скрипт копирует БД в `backups/`, хранит последние 10 копий и удаляет
файлы старше 30 дней.

## Лицензия

Проект создан для образовательных целей.

## Автор

AI-Органайзер — проект курса по разработке AI-приложений.
