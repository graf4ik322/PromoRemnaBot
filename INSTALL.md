# Установка Remnawave Telegram Bot

Подробное руководство по установке и настройке бота.

## Системные требования

- **Операционная система:** Linux (Ubuntu 20.04+ рекомендуется)
- **Python:** 3.9+
- **Память:** минимум 512MB RAM
- **Место на диске:** минимум 1GB свободного места
- **Сеть:** доступ к интернету для работы с Telegram API и Remnawave API

## Быстрая установка

### 🐳 Установка с Docker (рекомендуется)

```bash
# 1. Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Перелогиньтесь после выполнения

# 2. Получение исходного кода
git clone <repository-url>
cd remnawave-telegram-bot

# 3. Настройка конфигурации
cp .env.example .env
nano .env

# 4. Запуск бота
./docker-scripts/start.sh

# Для продакшен среды:
./docker-scripts/start.sh --prod
```

### 📦 Ручная установка

#### 1. Получение исходного кода

```bash
git clone <repository-url>
cd remnawave-telegram-bot
```

#### 2. Установка зависимостей

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install python3 python3-pip python3-venv -y

# Установка зависимостей Python
pip3 install -r requirements.txt
```

#### 3. Настройка конфигурации

```bash
# Копирование шаблона конфигурации
cp .env.example .env

# Редактирование конфигурации
nano .env
```

### 4. Настройка Telegram бота

1. Создайте бота у [@BotFather](https://t.me/botfather)
2. Выполните команду `/newbot`
3. Укажите имя и username бота
4. Получите токен бота
5. Добавьте токен в файл `.env`

### 5. Получение ID пользователей

Для получения ID пользователей Telegram:

```bash
# Запустите временно бота для получения ID
python3 -c "
import logging
from telegram.ext import Application, MessageHandler, filters

logging.basicConfig(level=logging.INFO)

async def get_user_id(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username
    print(f'User ID: {user_id}, Username: @{username}')

app = Application.builder().token('YOUR_BOT_TOKEN').build()
app.add_handler(MessageHandler(filters.TEXT, get_user_id))
print('Send any message to the bot to get your ID...')
app.run_polling()
"
```

### 6. Настройка Remnawave API

1. Откройте панель Remnawave
2. Перейдите в настройки API
3. Создайте новый API ключ
4. Скопируйте токен в файл `.env`

### 7. Тестирование установки

```bash
# Запуск тестов
python3 test_bot.py

# Если тесты прошли успешно, запустите бота
python3 main.py
```

## Детальная конфигурация

### Файл .env

```env
# Обязательные параметры
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
REMNAWAVE_BASE_URL=https://your-panel.domain.com
REMNAWAVE_TOKEN=your_remnawave_api_token
ADMIN_USER_IDS=123456789,987654321

# Дополнительные параметры
REMNAWAVE_CADDY_TOKEN=your_caddy_token
DEFAULT_INBOUND_IDS=1,2,3
DEFAULT_PROTOCOL=vless
DEFAULT_UUID_PREFIX=promo-
SUBSCRIPTION_FILE_BASE_URL=https://your-file-server.com/files/
MAX_SUBSCRIPTIONS_PER_REQUEST=100
LOG_LEVEL=INFO
```

### Параметры конфигурации

#### TELEGRAM_BOT_TOKEN
- **Описание:** Токен Telegram бота
- **Получение:** [@BotFather](https://t.me/botfather)
- **Формат:** `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

#### REMNAWAVE_BASE_URL
- **Описание:** URL панели Remnawave
- **Формат:** `https://panel.example.com`
- **Требования:** Должен быть доступен по HTTPS

#### REMNAWAVE_TOKEN
- **Описание:** API токен для Remnawave
- **Получение:** Панель Remnawave → API Settings
- **Права:** Должен иметь права на создание/удаление пользователей

#### ADMIN_USER_IDS
- **Описание:** ID пользователей с доступом к боту
- **Формат:** `123456789,987654321` (через запятую)
- **Получение:** Отправьте `/start` боту для получения ID

#### DEFAULT_INBOUND_IDS
- **Описание:** ID инбаундов для создания пользователей
- **Формат:** `1,2,3` (через запятую)
- **Получение:** Панель Remnawave → Inbounds

#### SUBSCRIPTION_FILE_BASE_URL
- **Описание:** Базовый URL для файлов подписок
- **Формат:** `https://files.example.com/`
- **Примечание:** Должен заканчиваться на `/`

## Автозапуск (systemd)

### 1. Создание службы

```bash
# Копирование файла службы
sudo cp remnawave-bot.service /etc/systemd/system/

# Редактирование путей в файле службы
sudo nano /etc/systemd/system/remnawave-bot.service
```

### 2. Настройка службы

Отредактируйте следующие строки в файле службы:

```ini
User=your_username
WorkingDirectory=/full/path/to/remnawave-telegram-bot
ExecStart=/usr/bin/python3 /full/path/to/remnawave-telegram-bot/main.py
ReadWritePaths=/full/path/to/remnawave-telegram-bot
```

### 3. Активация службы

```bash
# Перезагрузка systemd
sudo systemctl daemon-reload

# Включение автозапуска
sudo systemctl enable remnawave-bot

# Запуск службы
sudo systemctl start remnawave-bot

# Проверка статуса
sudo systemctl status remnawave-bot
```

### 4. Управление службой

```bash
# Запуск
sudo systemctl start remnawave-bot

# Остановка
sudo systemctl stop remnawave-bot

# Перезапуск
sudo systemctl restart remnawave-bot

# Просмотр логов
sudo journalctl -u remnawave-bot -f
```

## Безопасность

### Файервол

```bash
# Если используется ufw
sudo ufw allow ssh
sudo ufw allow 443/tcp
sudo ufw enable
```

### Права доступа

```bash
# Установка правильных прав на файлы
chmod 600 .env
chmod +x main.py
chmod +x run_bot.sh
```

### SSL/TLS

Убедитесь, что панель Remnawave доступна по HTTPS с валидным сертификатом.

## Мониторинг

### Логи бота

```bash
# Просмотр логов бота
tail -f bot.log

# Логи systemd
sudo journalctl -u remnawave-bot -f
```

### Проверка работоспособности

```bash
# Тест конфигурации
python3 test_bot.py

# Проверка процесса
ps aux | grep main.py

# Проверка портов (если нужно)
netstat -tulpn | grep python
```

## Обновление

### Обновление кода

```bash
# Остановка бота
sudo systemctl stop remnawave-bot

# Создание бэкапа
cp -r /path/to/bot /path/to/bot.backup

# Обновление из git
git pull origin main

# Установка новых зависимостей
pip3 install -r requirements.txt

# Запуск тестов
python3 test_bot.py

# Запуск бота
sudo systemctl start remnawave-bot
```

### Обновление зависимостей

```bash
# Обновление pip
pip3 install --upgrade pip

# Обновление зависимостей
pip3 install --upgrade -r requirements.txt
```

## Устранение проблем

### Проблемы с зависимостями

```bash
# Переустановка зависимостей
pip3 uninstall -r requirements.txt -y
pip3 install -r requirements.txt
```

### Проблемы с правами

```bash
# Проверка владельца файлов
ls -la

# Изменение владельца
sudo chown -R $USER:$USER .
```

### Проблемы с сетью

```bash
# Проверка доступности Telegram API
curl -I https://api.telegram.org

# Проверка доступности Remnawave
curl -I https://your-panel.domain.com
```

### Проблемы с памятью

```bash
# Проверка использования памяти
free -h

# Проверка swap
swapon --show

# Создание swap файла (если нужно)
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## Контакты и поддержка

При возникновении проблем:

1. Проверьте логи: `tail -f bot.log`
2. Запустите тесты: `python3 test_bot.py`
3. Проверьте статус службы: `sudo systemctl status remnawave-bot`
4. Создайте issue в репозитории проекта

---

**Примечание:** Этот бот предназначен только для авторизованных пользователей. Убедитесь, что вы правильно настроили `ADMIN_USER_IDS` для ограничения доступа.