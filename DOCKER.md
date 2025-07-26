# Docker руководство для Remnawave Telegram Bot

Полное руководство по развертыванию и управлению ботом с помощью Docker.

## 🚀 Быстрый старт

### Установка Docker

#### Ubuntu/Debian
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиньтесь для применения изменений
```

#### CentOS/RHEL
```bash
# Установка Docker
sudo yum install -y docker

# Запуск и автозапуск Docker
sudo systemctl start docker
sudo systemctl enable docker

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER
```

### Проверка установки
```bash
docker --version
docker-compose --version
# или для новых версий Docker
docker compose version
```

## 📦 Развертывание бота

### 1. Подготовка проекта
```bash
# Клонирование репозитория
git clone https://github.com/graf4ik322/PromoRemnaBot.git
cd PromoRemnaBot

# Создание .env файла
cp .env.example .env

# Редактирование конфигурации
nano .env
```

### 2. Development режим

```bash
# Запуск с помощью скрипта (рекомендуется)
./docker-scripts/start.sh

# Или вручную
docker-compose up --build -d

# Просмотр логов
docker logs promo-remna-bot -f
```

### 3. Production режим

```bash
# Запуск production версии
./docker-scripts/start.sh --prod

# Или вручную
docker-compose -f docker-compose.prod.yml up --build -d
```

## 🔧 Конфигурация

### Docker Compose файлы

#### Development (`docker-compose.yml`)
- Базовые настройки ресурсов
- Простая конфигурация логирования
- Быстрый запуск для разработки

#### Production (`docker-compose.prod.yml`)
- Увеличенные лимиты ресурсов
- Расширенное логирование
- Автоматические обновления (Watchtower)
- Дополнительные security настройки

### Переменные окружения

Основные переменные для Docker:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token

# Remnawave API
REMNAWAVE_BASE_URL=https://your-panel.domain.com
REMNAWAVE_TOKEN=your_api_token
REMNAWAVE_CADDY_TOKEN=your_caddy_token

# Admin settings
ADMIN_USER_IDS=123456789,987654321

# Limits
MAX_SUBSCRIPTIONS_PER_REQUEST=100

# Logging
LOG_LEVEL=INFO
```

### Тома и хранение данных

```yaml
volumes:
  - ./subscription_files:/app/subscription_files  # Файлы подписок
  - ./logs:/app/logs                              # Логи приложения
  - ./bot.log:/app/bot.log                        # Основной лог файл
```

## 🛠 Управление контейнерами

### Основные команды

```bash
# Запуск
./docker-scripts/start.sh              # Development
./docker-scripts/start.sh --prod       # Production

# Остановка
./docker-scripts/stop.sh               # Development
./docker-scripts/stop.sh --prod        # Production
./docker-scripts/stop.sh --remove-volumes  # С удалением volumes

# Перезапуск
docker-compose restart remnawave-bot

# Пересборка
docker-compose up --build -d
```

### Просмотр логов

```bash
# Все логи
docker logs promo-remna-bot

# Последние 100 строк
docker logs promo-remna-bot --tail 100

# Следить за логами в реальном времени
docker logs promo-remna-bot -f

# Логи с определенного времени
docker logs promo-remna-bot --since="2024-01-01T00:00:00"
```

### Вход в контейнер

```bash
# Интерактивный shell
docker exec -it promo-remna-bot bash

# Выполнение команды
docker exec promo-remna-bot python3 test_bot.py

# Просмотр процессов
docker exec promo-remna-bot ps aux
```

## 📊 Мониторинг

### Статус контейнеров

```bash
# Список запущенных контейнеров
docker ps

# Статус через docker-compose
docker-compose ps

# Детальная информация
docker inspect promo-remna-bot
```

### Использование ресурсов

```bash
# Статистика в реальном времени
docker stats promo-remna-bot

# Использование диска
docker system df

# Информация об образах
docker images
```

### Health checks

```bash
# Проверка здоровья контейнера
docker inspect promo-remna-bot | grep Health -A 10

# Ручная проверка
docker exec promo-remna-bot python3 -c "import requests; requests.get('https://api.telegram.org')"
```

## 🔄 Обновление

### Обновление кода

```bash
# Остановка контейнеров
./docker-scripts/stop.sh

# Обновление кода
git pull origin main

# Пересборка и запуск
./docker-scripts/start.sh --prod
```

### Автоматические обновления

Production конфигурация включает Watchtower для автоматических обновлений:

```yaml
watchtower:
  image: containrrr/watchtower
  environment:
    - WATCHTOWER_CLEANUP=true
    - WATCHTOWER_POLL_INTERVAL=86400  # Проверка раз в день
```

Отключение автообновлений:
```bash
# Редактирование docker-compose.prod.yml
# Закомментируйте секцию watchtower
```

## 🧹 Очистка

### Очистка контейнеров

```bash
# Остановка всех контейнеров
docker stop $(docker ps -aq)

# Удаление неиспользуемых контейнеров
docker container prune -f

# Удаление неиспользуемых образов
docker image prune -f

# Удаление всех неиспользуемых ресурсов
docker system prune -f
```

### Полная очистка проекта

```bash
# Остановка и удаление с volumes
./docker-scripts/stop.sh --remove-volumes

# Удаление образов проекта
docker rmi promo-remna-bot_remnawave-bot

# Очистка system
docker system prune -a -f
```

## 🔒 Безопасность

### Настройки безопасности

Production конфигурация включает:

```yaml
security_opt:
  - no-new-privileges:true    # Запрет повышения привилегий
read_only: false              # Файловая система только для чтения
tmpfs:
  - /tmp                      # Временные файлы в памяти
```

### Сетевая безопасность

```yaml
networks:
  remnawave-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16  # Изолированная сеть
```

### Рекомендации

1. **Регулярные обновления**: Обновляйте базовые образы
2. **Мониторинг логов**: Следите за подозрительной активностью  
3. **Ограничение ресурсов**: Настройте лимиты памяти и CPU
4. **Секреты**: Используйте Docker secrets для чувствительных данных

## ⚡ Оптимизация производительности

### Настройки ресурсов

```yaml
# Development
resources:
  limits:
    memory: 512M
    cpus: '0.5'

# Production  
resources:
  limits:
    memory: 1G
    cpus: '1.0'
```

### Оптимизация образа

```dockerfile
# Мультистейдж сборка
FROM python:3.11-slim as builder
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
```

### Кэширование

```bash
# Принудительная пересборка без кэша
docker-compose build --no-cache

# Очистка кэша сборки
docker builder prune -f
```

## 🐞 Отладка

### Отладка проблем

```bash
# Проверка конфигурации
docker-compose config

# Проверка переменных окружения
docker exec promo-remna-bot env

# Проверка файловой системы
docker exec promo-remna-bot ls -la /app

# Проверка сетевого подключения
docker exec promo-remna-bot curl -I https://api.telegram.org
```

### Логи отладки

```bash
# Включение debug логирования
# В .env файле:
LOG_LEVEL=DEBUG

# Перезапуск с новыми настройками
docker-compose restart remnawave-bot
```

### Тестирование

```bash
# Запуск тестов в контейнере
docker exec promo-remna-bot python3 test_bot.py

# Интерактивное тестирование
docker exec -it promo-remna-bot python3
```

## 📋 Troubleshooting

### Частые проблемы

#### 1. Контейнер не запускается
```bash
# Проверка логов
docker logs promo-remna-bot

# Проверка конфигурации .env
cat .env

# Проверка прав доступа
ls -la .env
```

#### 2. Проблемы с сетью
```bash
# Проверка сетей Docker
docker network ls

# Проверка подключения к API
docker exec promo-remna-bot curl -v https://api.telegram.org
```

#### 3. Проблемы с volumes
```bash
# Проверка volumes
docker volume ls

# Проверка монтирования
docker exec promo-remna-bot df -h
```

#### 4. Высокое потребление ресурсов
```bash
# Мониторинг ресурсов
docker stats --no-stream

# Анализ использования памяти
docker exec promo-remna-bot free -h
```

### Получение помощи

```bash
# Информация о системе
docker info

# Версии
docker version
docker-compose version

# Логи Docker daemon
sudo journalctl -u docker.service -f
```

## 🎯 Лучшие практики

### Development

1. Используйте `.dockerignore` для исключения ненужных файлов
2. Монтируйте код как volume для быстрой разработки
3. Используйте отдельные compose файлы для разных сред

### Production

1. Используйте конкретные версии образов (не `latest`)
2. Настройте health checks
3. Ограничьте ресурсы контейнеров
4. Используйте restart policies
5. Настройте централизованное логирование

### Безопасность

1. Запускайте контейнеры от непривилегированного пользователя
2. Используйте read-only файловые системы где возможно
3. Ограничьте capabilities
4. Сканируйте образы на уязвимости

---

**Примечание**: Этот бот оптимизирован для работы в Docker среде и готов к использованию в продакшн окружении с минимальными настройками.