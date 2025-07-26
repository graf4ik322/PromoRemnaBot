# API Testing и Troubleshooting Guide

## 🧪 Тестирование API подключения

### Быстрая диагностика

```bash
# 1. Проверьте подключение к API
docker exec promo-remna-bot python3 test_api.py

# 2. Проверьте конфигурацию
docker exec promo-remna-bot python3 -c "
from config import Config
print(f'Base URL: {Config.REMNAWAVE_BASE_URL}')
print(f'Token configured: {bool(Config.REMNAWAVE_TOKEN)}')
print(f'Admin IDs: {Config.ADMIN_USER_IDS}')
"

# 3. Проверьте логи на ошибки API
docker logs promo-remna-bot | grep -i "api\|remnawave\|error"
```

### Детальная диагностика

```bash
# Запустите комплексный тест API
docker exec -it promo-remna-bot python3 test_api.py

# Проверьте доступность SDK методов
docker exec promo-remna-bot python3 -c "
import asyncio
from remnawave_api import RemnawaveSDK
from config import Config

async def test_methods():
    sdk = RemnawaveSDK(Config.REMNAWAVE_BASE_URL, Config.REMNAWAVE_TOKEN)
    print('Available user methods:', [m for m in dir(sdk.users) if not m.startswith('_')])

asyncio.run(test_methods())
"
```

## 🔧 Исправленные проблемы API

### 1. Неправильные методы API

**❌ До исправления:**
```python
users_response = await self.sdk.users.get_users()
for user in users_response:
    username = user.get('username', '')
```

**✅ После исправления:**
```python
users_response = await self.sdk.users.get_all_users_v2()
for user in users_response.users:
    username = getattr(user, 'username', '')
```

### 2. Структура данных

**❌ Неправильно:**
- `response` - прямой список пользователей
- `user.get('field')` - доступ как к словарю

**✅ Правильно:**
- `response.users` - список пользователей в атрибуте объекта
- `getattr(user, 'field', default)` - доступ к атрибутам объекта

### 3. Проверка существования данных

**❌ Неправильно:**
```python
if not users_response:
    return []
```

**✅ Правильно:**
```python
if not users_response or not users_response.users:
    return []
```

## 📋 Тестирование функций бота

### Проверка поиска тегов

```bash
# Тест через Docker
docker exec promo-remna-bot python3 -c "
import asyncio
from remnawave_service import RemnawaveService

async def test_tags():
    service = RemnawaveService()
    tags = await service.get_tags_with_stats()
    print(f'Found {len(tags)} tags:', [t['tag'] for t in tags])

asyncio.run(test_tags())
"
```

### Проверка создания пользователей

```bash
# Проверка доступных методов создания
docker exec promo-remna-bot python3 -c "
import asyncio
from remnawave_api import RemnawaveSDK
from config import Config

async def check_create_methods():
    sdk = RemnawaveSDK(Config.REMNAWAVE_BASE_URL, Config.REMNAWAVE_TOKEN)
    methods = [m for m in dir(sdk.users) if 'create' in m.lower()]
    print('Create methods:', methods)

asyncio.run(check_create_methods())
"
```

## 🐛 Распространенные ошибки

### 1. AttributeError: 'list' object has no attribute 'users'

**Причина:** Старый API возвращал прямой список, новый возвращает объект с атрибутом `users`.

**Решение:** Обновите код на использование `response.users`.

### 2. TypeError: argument of type 'NoneType' is not iterable

**Причина:** API вернул None вместо ожидаемого ответа.

**Решение:** Добавьте проверки:
```python
if not response or not hasattr(response, 'users') or not response.users:
    return []
```

### 3. AttributeError: 'UserResponseDto' object has no attribute 'get'

**Причина:** Попытка использовать `.get()` на Pydantic объекте.

**Решение:** Используйте `getattr(user, 'field', default)`.

## 🔍 Отладка в реальном времени

### Логирование API вызовов

Добавьте в начало `remnawave_service.py`:

```python
import logging
logging.getLogger('remnawave_api').setLevel(logging.DEBUG)
```

### Проверка структуры ответа

```python
async def debug_api_response():
    sdk = RemnawaveSDK(Config.REMNAWAVE_BASE_URL, Config.REMNAWAVE_TOKEN)
    response = await sdk.users.get_all_users_v2()
    
    print(f"Response type: {type(response)}")
    print(f"Response attributes: {dir(response)}")
    
    if hasattr(response, 'users'):
        print(f"Users count: {len(response.users)}")
        if response.users:
            user = response.users[0]
            print(f"User type: {type(user)}")
            print(f"User attributes: {dir(user)}")
```

## ✅ Проверочный чеклист

- [ ] API base URL правильно настроен и доступен
- [ ] API token действителен и имеет необходимые права
- [ ] SDK инициализируется без ошибок  
- [ ] `get_all_users_v2()` возвращает данные
- [ ] Структура ответа содержит атрибут `users`
- [ ] Пользователи имеют ожидаемые атрибуты (username, disabled, etc.)
- [ ] Прomo-пользователи правильно идентифицируются по префиксу
- [ ] Теги извлекаются из имен пользователей корректно

## 🚀 Следующие шаги

После исправления API:
1. Проверьте что "Delete used subscriptions" находит теги
2. Убедитесь что создание промо-кампаний работает
3. Протестируйте статистику и предпросмотр удаления
4. Проверьте корректность подсчета активных/использованных подписок

## 📞 Получение помощи

Если проблемы остаются:

1. **Запустите диагностику:**
   ```bash
   docker exec promo-remna-bot python3 test_api.py > api_test_results.txt
   ```

2. **Соберите логи:**
   ```bash
   docker logs promo-remna-bot > bot_logs.txt
   ```

3. **Проверьте конфигурацию:**
   ```bash
   docker exec promo-remna-bot python3 -c "from config import Config; Config.validate()"
   ```

4. **Создайте issue** с приложенными файлами результатов тестов.