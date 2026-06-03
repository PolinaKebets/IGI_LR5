# 📦 Руководство по развёртыванию проекта ХимМаркет

## Содержание
1. [Подготовка проекта](#1-подготовка-проекта)
2. [Загрузка на GitHub](#2-загрузка-на-github)
3. [Деплой на Render.com](#3-деплой-на-rendercom)
4. [Сохранение данных базы данных](#4-сохранение-данных-базы-данных)
5. [Проверка работы](#5-проверка-работы)

---

## 1. Подготовка проекта

### 1.1. Проверка файлов

Убедитесь, что в папке `Polina` есть следующие файлы:

```
Polina/
├── chemshop/              # Настройки Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── store/                 # Основное приложение
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── templates/
│   └── ...
├── manage.py
├── requirements.txt       # ⚠️ ВАЖНО: зависимости
├── Dockerfile            # ⚠️ ВАЖНО: для Render
├── render.yaml           # ⚠️ ВАЖНО: конфигурация Render
├── .gitignore            # ⚠️ ВАЖНО: игнорирование файлов
├── db.sqlite3            # Локальная БД (не загружается на Render)
└── README.md
```

### 1.2. Проверка requirements.txt

Файл должен содержать:
```txt
Django==4.2
gunicorn
whitenoise
dj-database-url
psycopg2-binary
Pillow
django-crispy-forms
crispy-bootstrap4
requests
pytest
```

### 1.3. Проверка Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .

# Сборка статики
RUN python manage.py collectstatic --noinput

# Переменные окружения
ENV PYTHONUNBUFFERED=1

# Порт
EXPOSE 8000

# Запуск
CMD gunicorn --bind 0.0.0.0:8000 chemshop.wsgi:application
```

### 1.4. Проверка render.yaml

```yaml
services:
  - type: web
    name: chemmarket
    env: docker
    region: frankfurt
    plan: free
    branch: main
    healthCheckPath: /
    envVars:
      - key: PYTHONUNBUFFERED
        value: 1
      - key: DJANGO_SETTINGS_MODULE
        value: chemshop.settings
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
      - key: DATABASE_URL
        fromDatabase:
          name: chemmarket-db
          property: connectionString

databases:
  - name: chemmarket-db
    databaseName: chemmarket
    plan: free
```

---

## 2. Загрузка на GitHub

### 2.1. Инициализация репозитория

```bash
cd /Users/v.v.efremenko/Documents/bsuir/igi/LR5/Polina

# Инициализация Git
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: ХимМаркет проект"
```

### 2.2. Создание репозитория на GitHub

1. Откройте https://github.com/new
2. Введите имя репозитория: `chemmarket` или `django-store`
3. Выберите **Private** (приватный)
4. **НЕ** нажимайте "Add README" (у нас уже есть файлы)
5. Нажмите **Create repository**

### 2.3. Привязка и отправка

```bash
# Привязка удалённого репозитория
git remote add origin https://github.com/ВАШ_USERNAME/ВАШ_REPO.git

# Отправка кода
git branch -M main
git push -u origin main
```

### 2.4. Добавление преподавателя

1. Откройте репозиторий на GitHub
2. Перейдите в **Settings** → **Collaborators**
3. Нажмите **Add people**
4. Введите email преподавателя: `anzh52889@gmail.com`
5. Выберите роль **Read** (только просмотр)

---

## 3. Деплой на Render.com

### 3.1. Регистрация и подключение

1. Откройте https://render.com
2. Нажмите **Sign Up** → **Continue with GitHub**
3. Разрешите доступ к репозиториям

### 3.2. Создание сервиса

1. Нажмите **New +** → **Blueprint**
2. Выберите ваш репозиторий `chemmarket`
3. Нажмите **Connect**

### 3.3. Настройка переменных окружения

Render автоматически прочитает `render.yaml`, но проверьте:

| Ключ | Значение |
|------|----------|
| `SECRET_KEY` | (генерируется автоматически) |
| `DEBUG` | `false` |
| `DJANGO_SETTINGS_MODULE` | `chemshop.settings` |
| `DATABASE_URL` | (автоматически из БД) |

### 3.4. Запуск деплоя

1. Нажмите **Apply**
2. Render создаст:
   - Web Service (веб-приложение)
   - PostgreSQL Database (база данных)
3. Дождитесь завершения (5-10 минут)

### 3.5. Проверка логов

1. Откройте ваш сервис в дашборде
2. Перейдите во вкладку **Logs**
3. Убедитесь, что нет ошибок

---

## 4. Сохранение данных базы данных

### ⚠️ Важно

**SQLite (db.sqlite3) не переносится на Render!** Render использует PostgreSQL.

### 4.1. Экспорт данных из локальной БД

```bash
cd /Users/v.v.efremenko/Documents/bsuir/igi/LR5/Polina

# Активация venv
source /Users/v.v.efremenko/Documents/bsuir/igi/LR5/venv/bin/activate

# Создание фикстуры (дампа данных)
python manage.py dumpdata --format json --indent 2 \
    auth.User \
    store.Product \
    store.ProductCategory \
    store.Manufacturer \
    store.Customer \
    store.Employee \
    store.Order \
    store.OrderItem \
    store.PromoCode \
    store.Review \
    store.Article \
    store.Glossary \
    store.Contact \
    store.Vacancy \
    store.Company \
    store.CompanyHistory \
    store.PickupPoint \
    > fixtures/initial_data.json
```

### 4.2. Создание команды для загрузки данных

Создайте файл `store/management/commands/load_data.py`:

```python
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Загрузка данных из фикстуры'

    def add_arguments(self, parser):
        parser.add_argument('--fixture', type=str, default='initial_data.json')

    def handle(self, *args, **options):
        fixture = options['fixture']
        self.stdout.write(f'Загрузка данных из {fixture}...')
        call_command('loaddata', fixture)
        self.stdout.write(self.style.SUCCESS('Данные загружены успешно!'))
```

### 4.3. Автоматическая загрузка при деплое

Обновите `Dockerfile`:

```dockerfile
# ... после collectstatic ...

# Загрузка данных (если есть фикстура)
RUN if [ -f fixtures/initial_data.json ]; then \
    python manage.py load_data --fixture fixtures/initial_data.json || true; \
    fi
```

### 4.4. Альтернатива: seed_data

Если вы использовали `seed_data`:

```bash
# На Render (через SSH или консоль)
python manage.py seed_data
```

Или обновите `render.yaml`:

```yaml
services:
  - type: web
    name: chemmarket
    env: docker
    # ...
    dockerCommand: "python manage.py migrate --noinput && python manage.py seed_data && gunicorn --bind 0.0.0.0:8000 chemshop.wsgi:application"
```

### 4.5. Ручная загрузка данных на Render

1. Откройте дашборд Render
2. Выберите ваш сервис → **Shell**
3. Выполните команды:

```bash
# Загрузка фикстуры
python manage.py loaddata fixtures/initial_data.json

# Или запуск seed_data
python manage.py seed_data
```

---

## 5. Проверка работы

### 5.1. Проверка URL

Откройте в браузере:
```
https://chemmarket.onrender.com/
```

### 5.2. Тестирование функционала

| Страница | URL | Что проверить |
|----------|-----|---------------|
| Главная | `/` | Отображение товаров, время |
| Товары | `/products/` | Фильтры, поиск, сортировка |
| Вход | `/login/` | Вход как customer1/password123 |
| Профиль | `/profile/` | Данные покупателя, заказы |
| Админка | `/admin/` | admin/admin123 |

### 5.3. Проверка данных

1. Войдите как `customer1` / `password123`
2. Откройте `/profile/`
3. Проверьте:
   - ✅ Телефон, город, адрес
   - ✅ История заказов
   - ✅ Статусы заказов

### 5.4. Проверка базы данных

```bash
# Через Shell на Render
python manage.py shell

# В оболочке Python
from store.models import Product, Customer, Order
print(f"Товаров: {Product.objects.count()}")
print(f"Покупателей: {Customer.objects.count()}")
print(f"Заказов: {Order.objects.count()}")
```

---

## 🔧 Решение проблем

### Ошибка: "Database not found"

**Причина:** DATABASE_URL не настроен

**Решение:**
1. Render → Dashboard → Your Service → Environment
2. Добавьте `DATABASE_URL` из вашей базы данных

### Ошибка: "Static files not found"

**Причина:** collectstatic не выполнен

**Решение:**
```dockerfile
RUN python manage.py collectstatic --noinput
```

### Ошибка: "ModuleNotFoundError: psycopg2"

**Причина:** Нет драйвера PostgreSQL

**Решение:** Добавьте в `requirements.txt`:
```txt
psycopg2-binary==2.9.9
```

### Ошибка: "CSRF verification failed"

**Причина:** Не настроен CSRF

**Решение:** В `settings.py`:
```python
CSRF_TRUSTED_ORIGINS = ['https://*.onrender.com']
```

---

## 📋 Чек-лист перед сдачей

- [ ] Код загружен на GitHub
- [ ] Преподаватель добавлен как collaborator
- [ ] Проект развёрнут на Render
- [ ] Все страницы открываются (200 OK)
- [ ] База данных заполнена (товары, заказы, пользователи)
- [ ] Вход под customer1 работает
- [ ] Профиль отображает данные
- [ ] Фильтры и поиск работают
- [ ] Время в шапке отображается

---

## 📞 Контакты

Если возникли проблемы:
1. Проверьте логи на Render (Logs tab)
2. Проверьте консоль Django (локально)
3. Убедитесь, что все миграции применены

**Удачи с защитой! 🎓**
