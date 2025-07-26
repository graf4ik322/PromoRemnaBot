# 🚀 Быстрый старт - Remnawave Telegram Bot

Самый быстрый способ запустить бота с помощью Docker.

## ⚡ 5-минутная установка

### 1. Установка Docker (если не установлен)

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# После этого перелогиньтесь (выйдите и войдите снова)
```

### 2. Клонирование и настройка

```bash
# Клонирование репозитория
git clone <repository-url>
cd remnawave-telegram-bot

# Настройка окружения
cp .env.example .env
nano .env  # Отредактируйте настройки
```

### 3. Запуск бота

```bash
# Development режим
./docker-scripts/start.sh

# Production режим (рекомендуется)
./docker-scripts/start.sh --prod
```

### 4. Проверка работы

```bash
# Просмотр логов
docker logs remnawave-telegram-bot -f

# Статус контейнера
docker ps | grep remnawave

# Тестирование
docker exec remnawave-telegram-bot python3 test_bot.py
```

## ⚙️ Обязательные настройки .env

```env
# Получите у @BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# URL вашей панели Remnawave
REMNAWAVE_BASE_URL=https://your-panel.domain.com

# API токен (создайте в панели Remnawave)
REMNAWAVE_TOKEN=your_remnawave_api_token

# Ваш Telegram ID (отправьте /start боту для получения)
ADMIN_USER_IDS=123456789
```

## 🛠 Управление ботом

```bash
# Остановка
./docker-scripts/stop.sh

# Перезапуск
./docker-scripts/stop.sh && ./docker-scripts/start.sh --prod

# Просмотр логов
docker logs remnawave-telegram-bot -f

# Вход в контейнер
docker exec -it remnawave-telegram-bot bash

# Обновление
git pull && ./docker-scripts/start.sh --prod
```

## 📊 Мониторинг

```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats remnawave-telegram-bot

# Health check
docker inspect remnawave-telegram-bot | grep Health -A 5
```

## 🐞 Решение проблем

### Бот не запускается

```bash
# Проверьте логи
docker logs remnawave-telegram-bot

# Проверьте конфигурацию
cat .env

# Проверьте соединение с Remnawave
curl -I https://your-panel.domain.com
```

### Ошибки API

```bash
# Проверьте токен бота
curl -s "https://api.telegram.org/bot<YOUR_TOKEN>/getMe" | jq

# Тест подключения к Remnawave
docker exec remnawave-telegram-bot curl -I https://your-panel.domain.com
```

### Высокое потребление ресурсов

```bash
# Мониторинг ресурсов
docker stats --no-stream remnawave-telegram-bot

# Перезапуск с ограничениями
# Отредактируйте docker-compose.yml, измените limits
```

## 🔄 Обновление

```bash
# Простое обновление
./docker-scripts/stop.sh
git pull origin main
./docker-scripts/start.sh --prod

# Обновление с пересборкой образа
./docker-scripts/stop.sh
docker-compose build --no-cache
./docker-scripts/start.sh --prod
```

## 🔐 Безопасность

- ✅ Используйте **только HTTPS** для Remnawave панели
- ✅ Создайте **отдельный API токен** только для бота
- ✅ Ограничьте **права API токена** только необходимыми
- ✅ Регулярно **обновляйте** бота и Docker образы
- ✅ Мониторьте **логи** на подозрительную активность

## 📝 Получение ID пользователей

```bash
# Временный скрипт для получения Telegram ID
python3 -c "
from telegram.ext import Application, MessageHandler, filters
import asyncio

async def get_id(update, context):
    print(f'User ID: {update.effective_user.id}, Name: {update.effective_user.first_name}')

app = Application.builder().token('YOUR_BOT_TOKEN').build()
app.add_handler(MessageHandler(filters.TEXT, get_id))
print('Отправьте любое сообщение боту для получения ID...')
app.run_polling()
"
```

## 🎯 Production рекомендации

1. **Используйте production режим**:
   ```bash
   ./docker-scripts/start.sh --prod
   ```

2. **Настройте автообновления** (включено по умолчанию в prod режиме)

3. **Мониторинг логов**:
   ```bash
   # Настройте log rotation
   sudo logrotate -f /etc/logrotate.conf
   ```

4. **Backup конфигурации**:
   ```bash
   # Регулярно делайте backup .env файла
   cp .env .env.backup.$(date +%Y%m%d)
   ```

5. **Мониторинг дискового пространства**:
   ```bash
   # Очистка старых логов Docker
   docker system prune -f
   ```

---

## 🎉 Готово!

После выполнения этих шагов ваш бот будет работать в Docker контейнере с:

- ✅ **Автоматическим перезапуском** при сбоях
- ✅ **Ограничением ресурсов** для стабильности
- ✅ **Health checks** для мониторинга
- ✅ **Централизованным логированием**
- ✅ **Изолированной сетью** для безопасности

Отправьте `/start` вашему боту в Telegram для проверки работоспособности! 🤖