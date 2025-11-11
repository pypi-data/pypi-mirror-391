# FIAS_RU 🇷🇺

**Максимально простой и удобный Python SDK для работы с ФИАС (Федеральная информационная адресная система)**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Особенности

- 🚀 **Максимально простой API** - начните работать за 2 строки кода
- 🧠 **Умный поиск** - автоматически определяет тип запроса (строка, ID, GUID, кадастровый номер)
- ⚡ **Быстрый** - connection pooling и rate limiting из коробки
- 💡 **Автокомплит** - как в Яндекс/Google картах
- 🔒 **Надёжный** - автоматические retry при сетевых ошибках
- 📦 **Нулевые зависимости** - только Python stdlib + httpx + pydantic
- 🎯 **Типизированный** - полная поддержка type hints для IDE
- 🔄 **Sync + Async** - работает в любом контексте

---

## 📦 Установка

```bash
pip install FIAS-RU
```

---

## 🚀 Быстрый старт

### 1. Получите токен

Зарегистрируйтесь и получите токен на [fias.nalog.ru](https://fias.nalog.ru/)

### 2. Настройте переменную окружения

```bash
export FIAS_TOKEN="your_token_here"
```

Или создайте `.env` файл:

```env
FIAS_TOKEN=your_token_here
```

### 3. Используйте!

```python
from FIAS_RU import SPAS

# Инициализация (автоматически читает токен из env)
spas = SPAS()

# Поиск адреса
address = spas.search("Москва, Тверская 1")
print(address.full_name)  # "г Москва, ул Тверская, д 1"
print(address.postal_code)  # "125009"
print(address.oktmo)  # "45000000"
```

---

## 📚 Примеры использования

### Умный поиск (автоопределение типа запроса)

```python
from FIAS_RU import SPAS

spas = SPAS()

# Поиск по строке
addr = spas.search("Москва, Тверская 1")

# Поиск по GUID
addr = spas.search("77000000-0000-0000-0000-000000000000")

# Поиск по кадастровому номеру
addr = spas.search("77:01:0001001:1")

# Поиск по ID
addr = spas.search(123456)
addr = spas.search("123456")  # Тоже работает!
```

### Автокомплит для форм ввода

```python
# Получить подсказки
hints = spas.autocomplete("Москва, Тв")

for hint in hints[:5]:
    print(hint.full_name)
    # г Москва, ул Тверская
    # г Москва, ул Тверская-Ямская 1-я
    # г Москва, ул Тверская-Ямская 2-я
    # ...

# С ограничением по уровню (только улицы)
hints = spas.autocomplete("Москва", up_to_level=7, limit=10)
```

### Быстрый доступ к деталям адреса

```python
address = spas.search("Москва, Красная площадь 1")

# Все детали доступны как свойства
print(address.postal_code)      # "109012"
print(address.oktmo)            # "45000000"
print(address.okato)            # "45000000000"
print(address.ifns_ul)          # "7701"
print(address.ifns_fl)          # "7701"
print(address.kladr_code)       # "7700000000000"
print(address.cadastral_number) # "77:01:0001001:1"

# Красивое представление
print(address.level_name)   # "Здание"
print(address.short_name)   # "Красная площадь 1" (без "г Москва")
```

### Работа с регионами

```python
# Получить все регионы РФ
regions = spas.get_regions()

for region in regions[:5]:
    print(f"{region.region_code}: {region.full_name}")
    # 01: Республика Адыгея
    # 02: Республика Башкортостан
    # 03: Республика Бурятия
    # ...
```

### Экспорт данных

```python
address = spas.search("Москва, Тверская 1")

# В словарь
data = address.to_dict()

# В JSON
json_str = address.to_json(indent=2)

# Только основные поля (без деталей)
data = address.to_dict(include_details=False)
```

### Обработка ошибок

```python
from FIAS_RU import SPAS, FIASError, FIASValidationError

spas = SPAS()

try:
    address = spas.search("Москва")
except FIASValidationError as e:
    print(f"Ошибка валидации: {e}")
except FIASError as e:
    print(f"Ошибка ФИАС: {e}")
```

### Context manager (автоматическое закрытие соединений)

```python
from FIAS_RU import SPAS

with SPAS() as spas:
    address = spas.search("Москва, Тверская 1")
    print(address.full_name)
# Соединения автоматически закрыты
```

### Настройка клиента

```python
from FIAS_RU import SPAS, AddressType

spas = SPAS(
    base_url="https://fias-public-service.nalog.ru",  # По умолчанию
    token="your_token",                                # Или из FIAS_TOKEN env
    timeout=60.0,                                      # Таймаут запросов (сек)
    max_retries=5,                                     # Количество повторов
    default_address_type=AddressType.ADMINISTRATIVE,   # Тип адреса по умолчанию
    max_connections=100,                               # Connection pool
    rate_limit_requests=100,                           # Лимит запросов
    rate_limit_window=60.0                             # За 60 секунд
)
```

---

## 🎯 Продвинутые примеры

### Batch поиск нескольких адресов

```python
from FIAS_RU import SPAS
from concurrent.futures import ThreadPoolExecutor

spas = SPAS()

addresses_to_search = [
    "Москва, Тверская 1",
    "Санкт-Петербург, Невский проспект 1",
    "Казань, Кремлевская 1"
]

# Параллельный поиск
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(spas.search, addresses_to_search))

for addr in results:
    if addr:
        print(f"{addr.full_name} - {addr.postal_code}")
```

### Создание формы автокомплита (Django/Flask)

```python
from flask import Flask, request, jsonify
from FIAS_RU import SPAS

app = Flask(__name__)
spas = SPAS()

@app.route('/api/address/autocomplete')
def autocomplete():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    hints = spas.autocomplete(query, limit=10)
    return jsonify([
        {
            'id': hint.id,
            'text': hint.full_name,
            'html': hint.html  # С подсветкой совпадений
        }
        for hint in hints
    ])

@app.route('/api/address/details/<int:address_id>')
def address_details(address_id):
    address = spas.search(address_id)
    if not address:
        return jsonify({'error': 'Not found'}), 404
    
    return jsonify(address.to_dict())
```

### Валидация адресов из файла

```python
from FIAS_RU import SPAS
import csv

spas = SPAS()

with open('addresses.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        address_str = row['address']
        
        try:
            address = spas.search(address_str)
            if address:
                print(f"✅ {address_str}")
                print(f"   → {address.full_name}")
                print(f"   → ОКТМО: {address.oktmo}")
            else:
                print(f"❌ {address_str} - не найден")
        except Exception as e:
            print(f"⚠️ {address_str} - ошибка: {e}")
```

---

## 🔧 Конфигурация

### Переменные окружения

```bash
# Обязательные
export FIAS_TOKEN="your_token_here"

# Опциональные
export FIAS_BASE_URL="https://fias-public-service.nalog.ru"  # По умолчанию
export FIAS_TIMEOUT=30                                         # Таймаут (сек)
export FIAS_MAX_RETRIES=3                                      # Количество повторов
```

### Файл .env

```env
FIAS_TOKEN=your_token_here
FIAS_BASE_URL=https://fias-public-service.nalog.ru
FIAS_TIMEOUT=30
FIAS_MAX_RETRIES=3
```

---

## 📖 API Reference

### SPAS Client

#### `__init__(base_url=None, token=None, **kwargs)`

Инициализация клиента.

**Параметры:**
- `base_url` (str, optional): URL API. По умолчанию: публичный API ФНС
- `token` (str, optional): Токен авторизации. По умолчанию: из `FIAS_TOKEN` env
- `timeout` (float): Таймаут запросов в секундах (по умолчанию: 30)
- `max_retries` (int): Количество повторных попыток (по умолчанию: 3)
- `default_address_type` (AddressType): Тип адреса по умолчанию

#### `search(query, address_type=None) -> AddressItem | None`

Умный поиск адреса. Автоматически определяет тип запроса.

**Параметры:**
- `query` (str | int): Поисковый запрос (строка, ID, GUID, кадастровый номер)
- `address_type` (AddressType, optional): Тип адреса

**Возвращает:** `AddressItem` или `None`

#### `autocomplete(partial_address, limit=10, **kwargs) -> List[SearchHint]`

Автокомплит адреса.

**Параметры:**
- `partial_address` (str): Неполный адрес (минимум 1 символ)
- `limit` (int): Максимум подсказок (по умолчанию: 10)
- `address_type` (AddressType, optional): Тип адреса
- `up_to_level` (int, optional): До какого уровня искать

**Возвращает:** `List[SearchHint]`

#### `get_regions() -> List[AddressItem]`

Получить все регионы РФ.

**Возвращает:** `List[AddressItem]`

#### `get_details(address) -> AddressDetails | None`

Получить детали адреса (ОКТМО, ИФНС, почтовый индекс и т.д.).

**Параметры:**
- `address` (AddressItem | int): AddressItem или object_id

**Возвращает:** `AddressDetails` или `None`

### AddressItem

Адресный элемент с удобными свойствами.

**Основные поля:**
- `object_id` / `id` (int): ID объекта
- `object_guid` / `guid` (str): GUID объекта
- `full_name` (str): Полное название
- `short_name` (str): Короткое название (без типа)
- `level_name` (str): Название уровня ("Регион", "Город" и т.д.)
- `is_active` (bool): Активен ли адрес

**Быстрый доступ к деталям:**
- `postal_code` (str): Почтовый индекс
- `oktmo` (str): Код ОКТМО
- `okato` (str): Код ОКАТО
- `kladr_code` (str): Код КЛАДР
- `cadastral_number` (str): Кадастровый номер
- `ifns_ul` (str): ИФНС для юридических лиц
- `ifns_fl` (str): ИФНС для физических лиц

**Методы:**
- `to_dict(include_details=True)`: Преобразовать в словарь
- `to_json(indent=2)`: Преобразовать в JSON

---

## 🐛 Обработка ошибок

### Типы исключений

- `FIASError` - базовое исключение
- `FIASValidationError` - ошибка валидации входных данных
- `FIASAPIError` - ошибка API (5xx, проблемы с токеном)
- `FIASNetworkError` - сетевая ошибка
- `FIASTimeoutError` - таймаут запроса
- `FIASNotFoundError` - объект не найден

### Примеры

```python
from FIAS_RU import SPAS, FIASError, FIASValidationError, FIASAPIError

spas = SPAS()

try:
    address = spas.search("М")  # Слишком короткий запрос
except FIASValidationError as e:
    print(f"Ошибка валидации: {e}")

try:
    address = spas.search("Несуществующий адрес 12345")
except FIASAPIError as e:
    print(f"Ошибка API: {e}")

try:
    address = spas.search("Москва, Тверская 1")
except FIASError as e:
    print(f"Общая ошибка ФИАС: {e}")
```

---

## 🤝 Вклад в проект

Мы приветствуем вклад в проект! 

1. Fork репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Commit изменения (`git commit -m 'Add amazing feature'`)
4. Push в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

---

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

---

## 🔗 Полезные ссылки

- [Официальная документация ФИАС](https://fias.nalog.ru/)
- [API документация](https://fias.nalog.ru/docs)
- [GitHub репозиторий](https://github.com/PrimeevolutionZ/FIAS_RU)
- [PyPI пакет](https://pypi.org/project/FIAS-RU/)
- [Примеры использования](https://github.com/PrimeevolutionZ/FIAS_RU/tree/master/examples)
---

## ⭐ Поддержка

Если вам понравилась библиотека, поставьте звезду на GitHub!

Нашли баг? [Создайте issue](https://github.com/PrimeevolutionZ/FIAS_RU/issues)

---

**Сделано с ❤️ командой [Eclips](https://github.com/PrimeevolutionZ/FIAS_RU)**