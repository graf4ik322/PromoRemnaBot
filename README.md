# Remnawave Telegram Bot

Telegram бот для управления промо-кампаниями через панель Remnawave. Позволяет создавать промо-аккаунты, управлять подписками и получать статистику использования.

## Возможности

### 🎁 Создание промо-кампаний
- Ввод тега кампании с валидацией
- Выбор лимита трафика (15GB, 30GB, 50GB, 100GB)
- Создание от 1 до 100 подписок за раз
- Автоматическая генерация файла с подписками
- Отчет о создании с примерами ссылок

### 🗑 Удаление использованных подписок
- Просмотр всех тегов с статистикой
- Предпросмотр перед удалением
- Удаление только использованных подписок
- Детальный отчет об удалении

### 📊 Статистика
- Общая статистика по всем кампаниям
- Статистика по каждому тегу отдельно
- Информация об активных и использованных подписках

## Установка

### 🐳 Быстрый запуск с Docker (рекомендуется)

```bash
# 1. Клонирование репозитория
git clone https://github.com/graf4ik322/PromoRemnaBot.git
cd PromoRemnaBot

# 2. Настройка конфигурации
cp .env.example .env
# Отредактируйте .env файл с вашими настройками

# 3. Запуск бота (рекомендуется безопасный способ)
./docker-scripts/start-safe.sh --prod

# Диагностика проблем (если есть ошибки)
./docker-scripts/diagnose.sh

# Обычный запуск (если нет проблем с Docker)
./docker-scripts/start.sh --prod
```

### 📦 Ручная установка

#### 1. Клонирование репозитория
```bash
git clone https://github.com/graf4ik322/PromoRemnaBot.git
cd PromoRemnaBot
```

#### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

#### 3. Настройка конфигурации
Скопируйте файл `.env.example` в `.env` и заполните необходимые параметры:

```bash
cp .env.example .env
```

Отредактируйте файл `.env`:

```env
# Telegram Bot Token (получить у @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Remnawave Panel Configuration
REMNAWAVE_BASE_URL=https://your-panel.domain.com
REMNAWAVE_TOKEN=your_remnawave_api_token_here
REMNAWAVE_CADDY_TOKEN=your_caddy_token_here

# User Creation Settings
DEFAULT_INBOUND_IDS=1,2,3
DEFAULT_PROTOCOL=vless
DEFAULT_UUID_PREFIX=promo-
SUBSCRIPTION_FILE_BASE_URL=https://your-file-server.com/files/

# Limits and Settings
MAX_SUBSCRIPTIONS_PER_REQUEST=100
ADMIN_USER_IDS=123456789,987654321

# Logging
LOG_LEVEL=INFO
```

#### 4. Запуск бота
```bash
python main.py
```

## Конфигурация

### Обязательные параметры

- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `REMNAWAVE_BASE_URL` - URL панели Remnawave
- `REMNAWAVE_TOKEN` - API токен для Remnawave
- `ADMIN_USER_IDS` - ID пользователей с доступом к боту

### Дополнительные параметры

- `REMNAWAVE_CADDY_TOKEN` - токен для Caddy Auth (если используется)
- `DEFAULT_INBOUND_IDS` - ID инбаундов для создания пользователей
- `DEFAULT_PROTOCOL` - протокол по умолчанию
- `DEFAULT_UUID_PREFIX` - префикс для имен пользователей
- `SUBSCRIPTION_FILE_BASE_URL` - базовый URL для файлов подписок
- `MAX_SUBSCRIPTIONS_PER_REQUEST` - максимальное количество подписок за раз
- `LOG_LEVEL` - уровень логирования

## Использование

### Команды бота

- `/start` - Запуск бота и отображение главного меню
- `/cancel` - Отмена текущей операции

### Навигация

Бот использует инлайн-клавиатуру для навигации. Все действия выполняются через кнопки:

1. **🎁 Создать промо-кампанию**
   - Введите тег кампании
   - Выберите лимит трафика
   - Укажите количество подписок
   - Подтвердите создание

2. **🗑 Удалить использованные подписки**
   - Выберите тег из списка
   - Просмотрите статистику
   - Подтвердите удаление

3. **📊 Статистика**
   - Просмотр общей статистики
   - Детали по каждому тегу

### Форматы данных

#### Тег кампании
- Только латинские буквы, цифры, подчеркивания и дефисы
- Пробелы заменяются на подчеркивания
- Примеры: `summer_sale`, `black-friday`, `new_year_2024`

#### Лимиты трафика
- 15GB, 30GB, 50GB, 100GB
- Автоматическое конвертирование в байты

#### Количество подписок
- От 1 до 100 (настраивается через `MAX_SUBSCRIPTIONS_PER_REQUEST`)

## Docker

### 🐳 Управление контейнерами

```bash
# Запуск в development режиме
./docker-scripts/start.sh

# Запуск в production режиме
./docker-scripts/start.sh --prod

# Остановка контейнеров
./docker-scripts/stop.sh

# Остановка production контейнеров
./docker-scripts/stop.sh --prod

# Просмотр логов
docker logs promo-remna-bot -f

# Вход в контейнер
docker exec -it promo-remna-bot bash
```

### 📊 Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats promo-remna-bot

# Health check
docker inspect promo-remna-bot | grep Health -A 10
```

## Архитектура

### Структура файлов

```
remnawave-telegram-bot/
├── 📄 main.py                    # Основной файл приложения
├── ⚙️ config.py                  # Конфигурация и настройки
├── 🤖 bot_handlers.py            # Обработчики команд бота
├── 🔌 remnawave_service.py       # Сервис для работы с Remnawave API
├── 🛠 utils.py                   # Вспомогательные функции
├── 📋 requirements.txt           # Зависимости Python
├── 📄 .env.example               # Пример файла конфигурации
├── 🐳 Dockerfile                 # Docker образ
├── 🐙 docker-compose.yml         # Docker Compose (development)
├── 🏭 docker-compose.prod.yml    # Docker Compose (production)
├── 📂 docker-scripts/            # Скрипты управления Docker
│   ├── start.sh                  # Запуск контейнеров
│   └── stop.sh                   # Остановка контейнеров
└── 📚 README.md                  # Документация
```

### Компоненты

- **Config** - управление конфигурацией из переменных окружения
- **BotHandlers** - обработчики команд и callback'ов Telegram
- **RemnawaveService** - интеграция с Remnawave API
- **FileManager** - управление файлами подписок
- **ProgressTracker** - отслеживание прогресса длительных операций

## Особенности реализации

### UI/UX
- ✅ Инлайн-меню во всех местах
- ✅ Редактирование сообщений вместо отправки новых
- ✅ Автоматическое удаление пользовательских сообщений
- ✅ Кнопка "Назад в главное меню" везде где нужно
- ✅ Понятная навигация и валидация ввода

### Функциональность
- ✅ Создание промо-аккаунтов с валидацией
- ✅ Выбор лимита трафика через кнопки
- ✅ Генерация файлов с подписками
- ✅ Удаление только использованных подписок
- ✅ Предпросмотр статистики перед удалением
- ✅ Полная обработка ошибок

### Безопасность
- ✅ Проверка прав доступа через ADMIN_USER_IDS
- ✅ Валидация всех входных данных
- ✅ Обработка всех исключений
- ✅ Логирование всех действий

## Логирование

Все действия бота логируются в файл `logs/bot.log` и консоль. Уровень логирования настраивается через `LOG_LEVEL`.

Примеры логов:
```
2024-01-01 12:00:00 - main - INFO - Bot started successfully
2024-01-01 12:01:00 - remnawave_service - INFO - Created user: promo-abc123-summer_sale
2024-01-01 12:02:00 - bot_handlers - INFO - Successfully created 10 users for tag 'summer_sale'
```

## Устранение неполадок

### Ошибки API
- Проверьте правильность `REMNAWAVE_BASE_URL` и `REMNAWAVE_TOKEN`
- Убедитесь, что панель Remnawave доступна
- Проверьте права доступа API токена

### Ошибки бота
- Проверьте правильность `TELEGRAM_BOT_TOKEN`
- Убедитесь, что бот запущен у @BotFather
- Проверьте сетевое соединение

### Ошибки конфигурации
- Убедитесь, что все обязательные параметры заполнены
- Проверьте формат ID пользователей в `ADMIN_USER_IDS`
- Проверьте формат `DEFAULT_INBOUND_IDS`

## Разработка

### Расширение функциональности

Для добавления новых функций:

1. Добавьте новые обработчики в `BotHandlers`
2. Расширьте `RemnawaveService` для новых API методов
3. Обновите клавиатуры и состояния разговора
4. Добавьте соответствующие паттерны в `main.py`

### Тестирование

Для тестирования рекомендуется:
- Использовать отдельный тестовый бот
- Настроить тестовую панель Remnawave
- Проверить все сценарии использования
- Протестировать обработку ошибок

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл LICENSE для подробностей.

## 🐞 Troubleshooting

### Проблемы с Docker

**Ошибка "http+docker":**
```bash
# Используйте безопасный запуск
./docker-scripts/start-safe.sh --prod

# Или диагностику
./docker-scripts/diagnose.sh
```

**Ошибка "invalid literal for int()":**
```bash
# Проверьте формат DEFAULT_INBOUND_IDS в .env
grep DEFAULT_INBOUND_IDS .env

# Исправьте формат (числа или UUID):
DEFAULT_INBOUND_IDS=1,2,3
# или
DEFAULT_INBOUND_IDS=b9811fcd-f20b-45c2-912a-fb21ab6c7664
```

**Ошибка "Is a directory: bot.log":**
```bash
# Исправьте проблему с логированием
./docker-scripts/cleanup.sh

# Или вручную:
docker-compose down -v
rm -rf bot.log
./docker-scripts/start-safe.sh --prod
```

**Docker daemon не запущен:**
```bash
sudo systemctl start docker
sudo usermod -aG docker $USER
newgrp docker
```

**Подробное руководство:**
- См. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) для полного руководства по устранению проблем

### Быстрые решения

1. **Диагностика:** `./docker-scripts/diagnose.sh`
2. **Безопасный запуск:** `./docker-scripts/start-safe.sh --prod`  
3. **Проверка логов:** `docker logs promo-remna-bot`
4. **Полная переустановка:** `docker system prune -a && ./docker-scripts/start-safe.sh --prod`

## Поддержка

При возникновении проблем:
1. **Запустите диагностику:** `./docker-scripts/diagnose.sh`
2. **Проверьте логи:** `docker logs promo-remna-bot` или `tail -f logs/bot.log`
3. **См. руководство:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
4. **Проверьте конфигурацию в .env файле**
5. **Создайте issue в репозитории проекта**