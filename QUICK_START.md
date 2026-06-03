# 🚀 Быстрый старт: GitHub + Render

## 1️⃣ GitHub (5 минут)

```bash
cd /Users/v.v.efremenko/Documents/bsuir/igi/LR5/Polina

git init
git add .
git commit -m "ХимМаркет: готово к сдаче"

# Создай репозиторий на github.com/new (Private!)
git remote add origin https://github.com/ТВОЙ_НИК/ТВОЙ_РЕПОЗИТОРИЙ.git
git branch -M main
git push -u origin main
```

**Добавь преподавателя:**
- GitHub → Settings → Collaborators → Add `anzh52889@gmail.com`

---

## 2️⃣ Render.com (10 минут)

1. **Регистрация:** https://render.com → Sign Up with GitHub
2. **New Blueprint:** Выбери свой репозиторий
3. **Apply:** Render сам всё настроит по `render.yaml`

**Жди 5-10 минут** пока создастся база и деплой.

---

## 3️⃣ Данные БД (автоматически)

Файл `fixtures/initial_data.json` уже содержит:
- ✅ 12 товаров
- ✅ 6 категорий
- ✅ 5 производителей
- ✅ 4 пункта выдачи
- ✅ 5 покупателей (customer1-5)
- ✅ 3 сотрудника (emp1-3)
- ✅ Заказы, промокоды, отзывы

**На Render:**
1. Dashboard → твой сервис → **Shell**
2. ```bash
   python manage.py load_data
   ```

---

## 4️⃣ Проверка

| Что | URL | Логин/Пароль |
|-----|-----|--------------|
| Сайт | `https://ТВОЙ-ПРОЕКТ.onrender.com/` | — |
| Вход | `/login/` | customer1 / password123 |
| Админка | `/admin/` | admin / admin123 |

---

## 🔧 Если что-то не так

**Ошибка БД:**
```bash
# В Shell на Render
python manage.py migrate
python manage.py seed_data
```

**Ошибка статики:**
```bash
# В Dockerfile проверь:
RUN python manage.py collectstatic --noinput
```

**Не пускает в профиль:**
- Войди как `customer1` / `password123`
- У админа (`admin`) нет профиля покупателя

---

## 📁 Что уже готово

- ✅ `requirements.txt` — все зависимости
- ✅ `Dockerfile` — сборка образа
- ✅ `render.yaml` — конфигурация Render
- ✅ `.gitignore` — db.sqlite3 не попадёт в git
- ✅ `fixtures/initial_data.json` — дамп базы
- ✅ `load_data.py` — команда загрузки данных

**Осталось:** запушить и задеплоить! 🎯
