# Troubleshooting Guide - PromoRemnaBot

Руководство по устранению проблем при запуске PromoRemnaBot через Docker.

## 🤖 Проблемы функциональности бота

### Ошибка: "Can't parse entities" или функционал не работает

**Симптомы:**
```
Can't parse entities: can't find end of the entity starting at byte offset 333
TelegramError: HTTP 400 Bad Request
Bot functionality not working, buttons don't respond
```

**Причина:**
Ошибки форматирования сообщений Telegram (смешанный Markdown/HTML, проблемные символы).

**Решения:**
```bash
# 1. Обновите до последней версии (исправлено)
git pull

# 2. Перезапустите бота
./docker-scripts/start-safe.sh --prod

# 3. Проверьте логи на ошибки парсинга
docker logs promo-remna-bot | grep -i "parse entities"

# 4. Если проблема остается, проверьте конфигурацию
./docker-scripts/diagnose.sh
```

**Детали исправления:** См. [TELEGRAM_FORMATTING_FIX.md](TELEGRAM_FORMATTING_FIX.md)

### Ошибка: Кнопки выбора трафика не работают

**Симптомы:**
```
После ввода тега и появления кнопок выбора трафика (15GB, 30GB, 50GB, 100GB),
при нажатии на любую кнопку ничего не происходит
```

**Причина:**
Неправильная конфигурация ConversationHandler - обработчик трафика был в fallbacks вместо states.

**Решения:**
```bash
# 1. Обновите до исправленной версии
git pull
./docker-scripts/start-safe.sh --prod

# 2. Проверьте что conversation flow работает
# /start → Create promo → Enter tag → Select traffic → должно работать!
```

**Исправлено:** Добавлено состояние WAITING_TRAFFIC и правильная конфигурация ConversationHandler.

### Ошибка: Бот не находит существующие теги пользователей

**Симптомы:**
```
При нажатии "🗑 Удалить использованные подписки" бот показывает 
"❌ Промо-кампании не найдены", хотя в базе есть пользователи с тегами
```

**Причина:**
Неправильные методы API и способ доступа к данным пользователей.

**Решения:**
```bash
# 1. Обновите до исправленной версии
git pull
./docker-scripts/start-safe.sh --prod

# 2. Проверьте API connectivity  
docker exec promo-remna-bot python3 test_api.py

# 3. Убедитесь в правильности конфигурации .env
grep -E "(REMNAWAVE_BASE_URL|REMNAWAVE_TOKEN)" .env
```

**Что было исправлено:**
- Использование `get_all_users_v2()` вместо `get_users()`
- Правильный доступ к атрибутам объектов пользователей  
- Корректная обработка структуры ответа API

### Ошибка: При подтверждении создания ничего не происходит

**Симптомы:**
```
1. Выбор трафика работает ✅
2. Ввод количества работает ✅  
3. При нажатии "✅ Подтвердить создание" ничего не происходит ❌
```

**Причина:**
Conversation заканчивался (ConversationHandler.END) сразу после ввода количества, 
до того как пользователь мог нажать кнопку подтверждения.

**Решение:**
```bash
# 1. Обновите до исправленной версии
git pull
./docker-scripts/start-safe.sh --prod

# 2. Проверьте что conversation flow работает
docker logs promo-remna-bot | grep -i "conversation\|state"
```

**Что было исправлено:**
- Добавлено состояние `WAITING_CONFIRMATION` в conversation flow
- `handle_count_input` теперь возвращает `WAITING_CONFIRMATION` вместо `ConversationHandler.END`
- `confirm_create_callback` перемещен в состояние `WAITING_CONFIRMATION`
- Conversation продолжается до пользовательского решения

## 🐳 Docker Проблемы

### Ошибка: "Not supported URL scheme http+docker"

**Симптомы:**
```
urllib3.exceptions.URLSchemeUnknown: Not supported URL scheme http+docker
docker.errors.DockerException: Error while fetching server API version: Not supported URL scheme http+docker
```

**Причины:**
- Конфликт версий Docker Compose
- Неправильная конфигурация Docker
- Проблемы с переменными окружения Docker

**Решения:**

#### 1. Обновите Docker Compose
```bash
# Удалите старую версию
sudo apt-get remove docker-compose

# Установите Docker Compose v2 (рекомендуется)
sudo apt-get update
sudo apt-get install docker-compose-plugin

# Или используйте официальный способ
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 2. Используйте альтернативный запуск
```bash
# Используйте безопасный скрипт запуска
./docker-scripts/start-safe.sh --prod

# Или запустите диагностику
./docker-scripts/diagnose.sh
```

#### 3. Переключитесь на Docker Compose v2
```bash
# Вместо docker-compose используйте:
docker compose up --build -d

# Проверьте версию
docker compose version
```

### Ошибка: "Docker daemon is not running"

**Симптомы:**
```
Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Решения:**
```bash
# Запустите Docker daemon
sudo systemctl start docker

# Включите автозапуск
sudo systemctl enable docker

# Проверьте статус
sudo systemctl status docker

# Если не помогает, перезапустите
sudo systemctl restart docker
```

### Ошибка: "Permission denied"

**Симптомы:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Решения:**
```bash
# Добавьте пользователя в группу docker
sudo usermod -aG docker $USER

# Примените изменения
newgrp docker

# Или перелогиньтесь
# logout && login

# Проверьте
docker ps
```

### Ошибка: "Port already in use"

**Симптомы:**
```
bind: address already in use
```

**Решения:**
```bash
# Найдите процесс, использующий порт
sudo netstat -tlnp | grep :8080
sudo lsof -i :8080

# Остановите конфликтующий контейнер
docker stop $(docker ps -q --filter "publish=8080")

# Или измените порт в docker-compose.yml
```

### Ошибка: "No space left on device"

**Симптомы:**
```
no space left on device
```

**Решения:**
```bash
# Очистите Docker
docker system prune -a

# Удалите неиспользуемые образы
docker image prune -a

# Удалите неиспользуемые тома
docker volume prune

# Проверьте место на диске
df -h
```

## ⚙️ Проблемы конфигурации

### Ошибка: "Required configuration field not set"

**Симптомы:**
```
ValueError: Required configuration field TELEGRAM_BOT_TOKEN is not set
```

**Решения:**
```bash
# Проверьте .env файл
cat .env

# Скопируйте пример, если нет .env
cp .env.example .env

# Отредактируйте настройки
nano .env
```

**Обязательные переменные:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
REMNAWAVE_BASE_URL=https://your-panel.domain.com
REMNAWAVE_TOKEN=your_api_token_here
ADMIN_USER_IDS=123456789,987654321
```

### Ошибка: "Permission denied" при записи логов

**Симптомы:**
```
Fatal error: [Errno 13] Permission denied: '/app/logs/bot.log'
```

**Причина:**
Контейнер не может записать в директорию logs/ из-за проблем с правами доступа.

**Решения:**
```bash
# 1. Исправьте права доступа
chmod 755 logs/ 2>/dev/null || sudo chmod 755 logs/

# 2. Пересоздайте директории с правильными правами
./docker-scripts/cleanup.sh

# 3. Или создайте вручную
rm -rf logs
mkdir -p logs
chmod 755 logs

# 4. Запустите заново
./docker-scripts/start-safe.sh --prod

# 5. Если проблема остается, проверьте SELinux (на некоторых системах)
sudo setsebool -P container_manage_cgroup on 2>/dev/null || true
```

### Ошибка: "Fatal error: [Errno 21] Is a directory"

**Симптомы:**
```
Fatal error: [Errno 21] Is a directory: '/app/bot.log'
```

**Причина:**
Docker создал директорию вместо файла лога из-за неправильного монтирования volume.

**Решения:**
```bash
# 1. Обновите до последней версии (исправлено)
git pull

# 2. Удалите старые контейнеры и volumes
docker-compose down -v

# 3. Удалите директорию bot.log если она существует
rm -rf bot.log

# 4. Запустите заново
./docker-scripts/start-safe.sh --prod

# 5. Логи теперь в logs/bot.log
tail -f logs/bot.log
```

### Ошибка: "ValueError: invalid literal for int() with base 10"

**Симптомы:**
```
ValueError: invalid literal for int() with base 10: 'b9811fcd-f20b-45c2-912a-fb21ab6c7664'
```

**Причина:**
В поле `DEFAULT_INBOUND_IDS` указан UUID, но код пытается преобразовать его в число.

**Решения:**
```bash
# Проверьте формат DEFAULT_INBOUND_IDS в .env файле
grep DEFAULT_INBOUND_IDS .env

# Используйте числовые ID:
DEFAULT_INBOUND_IDS=1,2,3

# Или UUID (поддерживается с версии v0.0.2+):
DEFAULT_INBOUND_IDS=b9811fcd-f20b-45c2-912a-fb21ab6c7664,another-uuid

# Обновите до последней версии:
git pull && ./docker-scripts/start-safe.sh --prod
```

### Ошибка: "Failed to connect to Remnawave API"

**Симптомы:**
```
ConnectionError: Failed to establish a new connection
```

**Решения:**
```bash
# Проверьте URL панели
curl -I https://your-panel.domain.com

# Проверьте токен API
curl -H "Authorization: Bearer your_token" https://your-panel.domain.com/api/health

# Проверьте настройки в .env
grep REMNAWAVE .env
```

## 🔧 Диагностика и отладка

### Автоматическая диагностика
```bash
# Запустите полную диагностику
./docker-scripts/diagnose.sh

# Проверьте логи контейнера
docker logs promo-remna-bot

# Войдите в контейнер для отладки
docker exec -it promo-remna-bot bash
```

### Ручная проверка

#### 1. Проверка Docker
```bash
# Версии
docker --version
docker-compose --version
docker compose version

# Информация о системе
docker info
docker system df
```

#### 2. Проверка контейнеров
```bash
# Список контейнеров
docker ps -a

# Статистика ресурсов
docker stats

# Логи
docker logs promo-remna-bot --tail 50
```

#### 3. Проверка сети
```bash
# Проверка подключения
curl -I https://api.telegram.org
curl -I https://your-panel.domain.com

# DNS
nslookup api.telegram.org
nslookup your-panel.domain.com
```

## 🚀 Альтернативные способы запуска

### 1. Безопасный запуск
```bash
# Используйте улучшенный скрипт
./docker-scripts/start-safe.sh --prod
```

### 2. Ручной запуск
```bash
# Создайте .env файл
cp .env.example .env
nano .env

# Создайте директории
mkdir -p subscription_files logs

# Проверьте синтаксис
docker compose -f docker-compose.prod.yml config

# Запустите контейнеры
docker compose -f docker-compose.prod.yml up --build -d
```

### 3. Запуск без Docker
```bash
# Установите зависимости
pip install -r requirements.txt

# Запустите напрямую
python3 main.py
```

## 🔍 Специфичные ошибки

### Ошибка импорта модулей
```bash
# Если ModuleNotFoundError
docker exec -it promo-remna-bot pip list
docker exec -it promo-remna-bot pip install -r requirements.txt
```

### Проблемы с health check
```bash
# Отключите health check временно
# В docker-compose.yml закомментируйте секцию healthcheck

# Или измените команду проверки
healthcheck:
  test: ["CMD", "python3", "-c", "print('OK')"]
```

### Проблемы с volumes
```bash
# Проверьте права доступа
ls -la subscription_files/ logs/

# Измените права, если нужно
chmod 755 subscription_files logs
chown -R $USER:$USER subscription_files logs
```

## 📞 Получение помощи

### Сбор информации для поддержки
```bash
# Соберите диагностическую информацию
./docker-scripts/diagnose.sh > diagnosis.txt

# Соберите логи
docker logs promo-remna-bot > bot-logs.txt 2>&1

# Информация о системе
uname -a > system-info.txt
docker info > docker-info.txt 2>&1
```

### Полезные команды для отладки
```bash
# Проверка конфигурации
docker compose config

# Пересборка без кэша
docker compose build --no-cache

# Запуск с выводом логов
docker compose up --build

# Остановка и удаление всего
docker compose down -v --remove-orphans
```

### Частые вопросы

**Q: Как полностью переустановить бота?**
```bash
# Остановите и удалите все
docker compose down -v --remove-orphans
docker system prune -a

# Удалите образы
docker rmi $(docker images -q)

# Запустите заново
./docker-scripts/start-safe.sh --prod
```

**Q: Как обновить бота?**
```bash
# Получите последние изменения
git pull

# Пересоберите образы
docker compose build --no-cache

# Перезапустите
docker compose up -d
```

**Q: Как изменить порты?**
```bash
# Отредактируйте docker-compose.yml
# Добавьте секцию ports:
ports:
  - "8080:8080"
```

## 🛠 Экстренные решения

### Если ничего не работает:
1. Остановите все контейнеры: `docker stop $(docker ps -q)`
2. Удалите все контейнеры: `docker rm $(docker ps -aq)`
3. Очистите систему: `docker system prune -a --volumes`
4. Перезапустите Docker: `sudo systemctl restart docker`
5. Используйте безопасный запуск: `./docker-scripts/start-safe.sh --prod`

### Если Docker Compose не работает:
1. Используйте Docker Compose v2: `docker compose` вместо `docker-compose`
2. Обновите Docker: `sudo apt update && sudo apt install docker-ce docker-compose-plugin`
3. Запустите вручную: `docker build -t promo-remna-bot . && docker run -d --env-file .env promo-remna-bot`

---

**💡 Совет:** Всегда сначала запускайте `./docker-scripts/diagnose.sh` для выявления проблем!