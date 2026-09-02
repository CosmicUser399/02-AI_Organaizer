# Docker инструкции для AI-Органайзер

## Быстрый старт

### 1. Подготовка

Убедитесь, что установлены Docker и Docker Compose:

```bash
docker --version
docker-compose --version
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_CHAT_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
API_BASE_URL=http://localhost:18080
```

### 3. Запуск приложения

#### Development режим (с hot-reload)

```bash
docker-compose up
```

Приложение будет доступно:
- Frontend: http://localhost:5173
- Backend API: http://localhost:18080
- API документация: http://localhost:18080/docs

#### Production режим

```bash
docker-compose -f docker-compose.prod.yml up -d
```

Приложение будет доступно:
- Frontend: http://localhost:80
- Backend API: http://localhost:18080

## Важное замечание о Docker-прокси

В development-режиме Vite проксирует `/api` на
`http://backend:18080`. Имя `backend` разрешается Docker только
внутри compose-сети, поэтому frontend в браузере должен обращаться
к относительному адресу `/api`, а не напрямую к
`http://backend:18080`.

Коллекционный маршрут задач FastAPI объявлен с завершающим `/`.
Для операций со списком frontend использует `/api/tasks/`:

- `GET /api/tasks/`
- `POST /api/tasks/`
- `DELETE /api/tasks/`

Это предотвращает HTTP 307 redirect на внутренний Docker-адрес
`backend:18080`.

## Основные команды

### Управление контейнерами

```bash
# Запуск в фоновом режиме
docker-compose up -d

# Остановка
docker-compose down

# Остановка с удалением volumes (БД будет очищена!)
docker-compose down -v

# Перезапуск конкретного сервиса
docker-compose restart backend
docker-compose restart frontend

# Просмотр статуса
docker-compose ps
```

### Просмотр логов

```bash
# Все логи
docker-compose logs

# Следить за логами в реальном времени
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs backend
docker-compose logs frontend

# Последние N строк
docker-compose logs --tail=100 backend
```

### Пересборка образов

```bash
# Пересобрать все образы
docker-compose build

# Пересобрать конкретный сервис
docker-compose build backend

# Пересобрать backend после изменения requirements.txt
docker-compose build --no-cache backend
docker-compose up -d backend

# Пересобрать без использования кеша
docker-compose build --no-cache

# Запустить с пересборкой
docker-compose up --build
```

### Выполнение команд внутри контейнеров

```bash
# Backend: запустить Python скрипт
docker-compose exec backend python -m some_module

# Backend: открыть Python REPL
docker-compose exec backend python

# Backend: запустить линтер
docker-compose exec backend ruff check app/

# Frontend: запустить линтер
docker-compose exec frontend npm run lint

# Frontend: установить новый пакет
docker-compose exec frontend npm install package-name

# Открыть shell в контейнере
docker-compose exec backend bash
docker-compose exec frontend sh
```

### Очистка

```bash
# Удалить все контейнеры, сети и volumes проекта
docker-compose down -v

# Удалить все неиспользуемые образы Docker
docker image prune -a

# Полная очистка Docker (осторожно!)
docker system prune -a --volumes
```

## Структура Docker конфигурации

### Backend Dockerfile

- Базовый образ: `python:3.11-slim`
- Устанавливает зависимости из `requirements.txt`
- Копирует код приложения
- Запускает uvicorn на порту 18080

### Frontend Dockerfile (multi-stage)

**Development stage:**
- Базовый образ: `node:18-alpine`
- Устанавливает зависимости
- Запускает Vite dev-сервер с hot-reload

**Production stage:**
- Builder: собирает статику с помощью Vite
- Production: nginx с собранными файлами
- Nginx проксирует `/api/` запросы к backend

### docker-compose.yml (Development)

- Backend: порт 18080, hot-reload через volume mount
- Frontend: порт 5173, hot-reload через volume mount
- Volumes для сохранения данных БД
- Health check для backend

### docker-compose.prod.yml (Production)

- Backend: оптимизированный образ без dev-зависимостей
- Frontend: nginx с минимальным образом
- Автоматический перезапуск контейнеров
- Frontend на порту 80

## Разработка с Docker

### Workflow для разработки

1. Запустите контейнеры в development режиме:
   ```bash
   docker-compose up
   ```

2. Редактируйте код локально — изменения будут автоматически
   применяться благодаря volume mount:
   - Backend: hot-reload через uvicorn --reload
   - Frontend: hot-reload через Vite HMR

3. Просматривайте логи в реальном времени:
   ```bash
   docker-compose logs -f
   ```

4. Для добавления новых зависимостей:
   - Backend: обновите `requirements.txt` и пересоберите:
     ```bash
     docker-compose build --no-cache backend
     docker-compose up -d backend
     ```
   - Frontend: обновите `package.json` и пересоберите:
     ```bash
     docker-compose build frontend
     docker-compose up -d frontend
     ```

### Отладка

```bash
# Проверить, что контейнеры запущены
docker-compose ps

# Проверить логи на ошибки
docker-compose logs backend | grep -i error
docker-compose logs frontend | grep -i error

# Проверить доступность backend API
curl http://localhost:18080/health

# Зайти внутрь контейнера для отладки
docker-compose exec backend bash
```

## Production развёртывание

### Подготовка

1. Настройте `.env` с production параметрами
2. Убедитесь, что все изменения зафиксированы в git

### Запуск

```bash
# Запустить в production режиме
docker-compose -f docker-compose.prod.yml up -d

# Проверить статус
docker-compose -f docker-compose.prod.yml ps

# Просмотреть логи
docker-compose -f docker-compose.prod.yml logs -f
```

### Обновление приложения

```bash
# 1. Получить новый код
git pull

# 2. Пересобрать образы
docker-compose -f docker-compose.prod.yml build

# 3. Перезапустить с новыми образами
docker-compose -f docker-compose.prod.yml up -d

# 4. Проверить, что всё работает
docker-compose -f docker-compose.prod.yml ps
curl http://localhost:18080/health
```

### Резервное копирование БД

```bash
# Скопировать БД из контейнера
docker cp ai-organizer-backend-prod:/app/data/app.db ./backup_$(date +%Y%m%d).db

# Восстановить БД
docker cp ./backup_20260902.db ai-organizer-backend-prod:/app/data/app.db
docker-compose -f docker-compose.prod.yml restart backend
```

## Troubleshooting

### Ошибка `unexpected keyword argument 'proxies'`

Эта ошибка означает несовместимость версии OpenAI SDK с `httpx`
или использование старого Docker-слоя зависимостей. В проекте
зафиксирована совместимая пара `openai==1.47.0` и `httpx==0.27.2`.
После изменения зависимостей выполните:

```bash
docker-compose build --no-cache backend
docker-compose up -d backend
docker-compose logs --since 1m backend
```

В логах должен появиться `Application startup complete`.

### Warning `validateDOMNesting` в React

MUI `ListItemText.secondary` по умолчанию создаёт HTML-элемент `<p>`.
Не помещайте внутрь него `Box`, `Chip` и другие блочные компоненты.
Размещайте такой контент отдельным соседом `ListItemText`.

### Контейнер не запускается

```bash
# Проверить логи
docker-compose logs backend

# Проверить, не занят ли порт
netstat -ano | findstr :18080  # Windows
lsof -i :18080                  # Linux/Mac

# Пересоздать контейнеры
docker-compose down
docker-compose up --force-recreate
```

### Frontend не может подключиться к Backend

1. Проверьте, что backend запущен:
   ```bash
   docker-compose ps backend
   curl http://localhost:18080/health
   ```

2. В development режиме Vite должен проксировать `/api` на backend
3. В production режиме nginx должен проксировать `/api` на backend

### База данных потеряна

Если вы случайно удалили volume с БД:

```bash
# БД создастся автоматически при следующем запуске
docker-compose up -d

# Данные будут потеряны, нужно восстановить из backup
```

### Проблемы с правами доступа (Linux)

```bash
# Если возникают проблемы с правами на созданные файлы
sudo chown -R $USER:$USER backend/data
```

## Полезные ссылки

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Vite Docker Guide](https://vitejs.dev/guide/static-deploy.html)
