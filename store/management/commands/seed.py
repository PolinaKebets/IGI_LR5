from __future__ import annotations

import random
from decimal import Decimal
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from store.models import (
    Company, CompanyHistory,
    Article, Glossary, Contact, Vacancy, Review, PromoCode,
    Manufacturer, ProductCategory, Product,
    PickupPoint, Customer, Employee,
    Order, OrderItem,
)


PHONE_POOL = [
    "+375 (29) 111-11-11",
    "+375 (29) 222-22-22",
    "+375 (25) 333-33-33",
    "+375 (25) 444-44-44",
    "+375 (29) 555-55-55",
    "+375 (25) 666-66-66",
]


class Command(BaseCommand):
    help = "Seed demo data for LR5 (store app)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete store data before seeding (keeps auth users).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        clear = options["clear"]

        if clear:
            self._clear_store_data()

        self.stdout.write("Seeding demo data...")

        users = self._create_users()
        company = self._create_company()
        self._create_company_history(company)
        self._create_articles(10)
        self._create_glossary(10)
        self._create_contacts()
        self._create_vacancies()
        promo_codes = self._create_promo_codes()
        manufacturers = self._create_manufacturers()
        categories = self._create_categories()
        products = self._create_products(categories, manufacturers, count=12)
        pickup_points = self._create_pickup_points()

        customers = self._create_customers(users["customers"], pickup_points)
        employees = self._create_employees(users["employees"])

        self._create_reviews(users["customers"])
        self._create_orders(customers, employees, products, promo_codes)

        self.stdout.write(self.style.SUCCESS("OK: database seeded."))

        self.stdout.write(
            self.style.WARNING(
                "Accounts:\n"
                "  admin / admin12345\n"
                "  customer1 / customer12345\n"
                "  employee1 / employee12345\n"
            )
        )

    def _clear_store_data(self):
        # порядок важен из-за FK
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        Review.objects.all().delete()

        Customer.objects.all().delete()
        Employee.objects.all().delete()

        Product.objects.all().delete()
        ProductCategory.objects.all().delete()
        Manufacturer.objects.all().delete()

        PromoCode.objects.all().delete()
        PickupPoint.objects.all().delete()

        Vacancy.objects.all().delete()
        Contact.objects.all().delete()
        Glossary.objects.all().delete()
        Article.objects.all().delete()

        CompanyHistory.objects.all().delete()
        Company.objects.all().delete()

        self.stdout.write(self.style.WARNING("Store data cleared."))

    def _create_users(self):
        User = get_user_model()

        # superuser
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@example.com",
                password="admin12345",
            )

        # customers
        customer_users = []
        for i in range(1, 6):
            username = f"customer{i}"
            u, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@example.com"},
            )
            if not u.has_usable_password():
                u.set_password("customer12345")
                u.save(update_fields=["password"])
            customer_users.append(u)

        # employees
        employee_users = []
        for i in range(1, 3):
            username = f"employee{i}"
            u, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@example.com"},
            )
            if not u.has_usable_password():
                u.set_password("employee12345")
                u.save(update_fields=["password"])
            employee_users.append(u)

        return {"customers": customer_users, "employees": employee_users}

    def _create_company(self):
        company, _ = Company.objects.get_or_create(
            name="ChemShop — магазин бытовой химии",
            defaults={
                "description": "Демонстрационная компания для ЛР №5.",
                "founded_year": 2015,
                "email": "info@chemshop.example.com",
                "phone": "+375 (29) 777-77-77",
                "address": "г. Минск, ул. Примерная, 1",
            },
        )
        return company

    def _create_company_history(self, company):
        years = [
            (2015, "Открытие интернет-магазина."),
            (2018, "Расширение ассортимента и поставщиков."),
            (2022, "Запуск программы лояльности и промокодов."),
            (2025, "Оптимизация логистики и самовывоза."),
        ]
        for y, ev in years:
            CompanyHistory.objects.get_or_create(company=company, year=y, defaults={"event": ev})

    def _create_articles(self, count: int):
        for i in range(1, count + 1):
            Article.objects.get_or_create(
                title=f"Новость №{i}",
                defaults={
                    "summary": f"Коротко о новости №{i} (демо).",
                    "content": f"Полный текст новости №{i}. Дата: {timezone.now().strftime('%d/%m/%Y')}.",
                    "is_published": True,
                },
            )

    def _create_glossary(self, count: int):
        for i in range(1, count + 1):
            Glossary.objects.get_or_create(
                question=f"Термин {i}",
                defaults={"answer": f"Определение/ответ для термина {i}."},
            )

    def _create_contacts(self):
        people = [
            ("Иван", "Петров", "Менеджер", "Консультации по товарам", PHONE_POOL[0], "ivan.petrov@example.com"),
            ("Анна", "Сидорова", "Оператор", "Поддержка клиентов", PHONE_POOL[1], "anna.sidorova@example.com"),
            ("Олег", "Иванов", "Логист", "Самовывоз и доставка", PHONE_POOL[2], "oleg.ivanov@example.com"),
        ]
        for fn, ln, pos, desc, phone, email in people:
            Contact.objects.get_or_create(
                first_name=fn,
                last_name=ln,
                defaults={
                    "position": pos,
                    "description": desc,
                    "phone": phone,
                    "email": email,
                },
            )

    def _create_vacancies(self):
        Vacancy.objects.get_or_create(title="Менеджер по продажам", defaults={"description": "Работа с заказами и клиентами.", "is_active": True})
        Vacancy.objects.get_or_create(title="Складской работник", defaults={"description": "Комплектация и учет товара.", "is_active": True})
        Vacancy.objects.get_or_create(title="Курьер", defaults={"description": "Доставка заказов.", "is_active": False})

    def _create_promo_codes(self):
        today = date.today()
        codes = [
            ("WELCOME10", "Скидка для новых клиентов", 10, today - timedelta(days=30), today + timedelta(days=365), True),
            ("SPRING15", "Весенняя акция", 15, today - timedelta(days=10), today + timedelta(days=20), True),
            ("OLD5", "Архивный промокод", 5, today - timedelta(days=400), today - timedelta(days=200), False),
        ]
        objs = []
        for code, desc, percent, vf, vt, active in codes:
            obj, _ = PromoCode.objects.get_or_create(
                code=code,
                defaults={
                    "description": desc,
                    "discount_percent": percent,
                    "valid_from": vf,
                    "valid_to": vt,
                    "is_active": active,
                },
            )
            objs.append(obj)
        return objs

    def _create_manufacturers(self):
        data = [
            ("CleanPro", "Польша", "https://example.com/cleanpro"),
            ("EcoHome", "Германия", "https://example.com/ecohome"),
            ("FreshLab", "Беларусь", "https://example.com/freshlab"),
        ]
        objs = []
        for name, country, site in data:
            obj, _ = Manufacturer.objects.get_or_create(
                name=name,
                defaults={"country": country, "website": site, "description": "Демо изготовитель."},
            )
            objs.append(obj)
        return objs

    def _create_categories(self):
        names = [
            ("Средства для кухни", "Гели, спреи, чистящие средства"),
            ("Стирка", "Порошки, гели, кондиционеры"),
            ("Санузел", "Средства от налета и извести"),
        ]
        objs = []
        for n, d in names:
            obj, _ = ProductCategory.objects.get_or_create(name=n, defaults={"description": d})
            objs.append(obj)
        return objs

    def _create_products(self, categories, manufacturers, count=10):
        base = [
            ("Гель для мытья посуды", "l", Decimal("6.50")),
            ("Спрей для стекол", "ml", Decimal("5.20")),
            ("Порошок стиральный", "kg", Decimal("18.90")),
            ("Кондиционер для белья", "l", Decimal("12.40")),
            ("Средство для сантехники", "l", Decimal("9.90")),
            ("Отбеливатель", "l", Decimal("7.30")),
            ("Универсальный очиститель", "l", Decimal("8.10")),
            ("Средство для плит", "ml", Decimal("6.90")),
            ("Мыло жидкое", "ml", Decimal("4.60")),
            ("Освежитель воздуха", "ml", Decimal("7.80")),
            ("Средство для полов", "l", Decimal("10.00")),
            ("Пятновыводитель", "ml", Decimal("8.70")),
        ][:count]

        objs = []
        for i, (name, unit, price) in enumerate(base, start=1):
            cat = random.choice(categories)
            obj, _ = Product.objects.get_or_create(
                name=name,
                defaults={
                    "category": cat,
                    "price": price,
                    "unit": unit,
                    "description": f"Демо-описание товара {i}.",
                    "stock_quantity": random.randint(5, 80),
                    "is_available": True,
                },
            )
            # ManyToMany
            obj.manufacturers.set(random.sample(manufacturers, k=random.randint(1, len(manufacturers))))
            objs.append(obj)
        return objs

    def _create_pickup_points(self):
        data = [
            ("Минск", "ул. Ленина, 10", PHONE_POOL[3], "10:00-20:00"),
            ("Минск", "пр-т Независимости, 55", PHONE_POOL[4], "09:00-21:00"),
            ("Гродно", "ул. Советская, 1", PHONE_POOL[5], "10:00-19:00"),
        ]
        objs = []
        for city, address, phone, hours in data:
            obj, _ = PickupPoint.objects.get_or_create(
                city=city,
                address=address,
                defaults={"phone": phone, "working_hours": hours},
            )
            objs.append(obj)
        return objs

    def _create_customers(self, users, pickup_points):
        customers = []
        # всем сделаем возраст 18+
        birth_dates = [
            date(1999, 5, 20),
            date(1995, 1, 15),
            date(1990, 9, 2),
            date(2000, 3, 11),
            date(1998, 12, 30),
        ]
        for i, u in enumerate(users):
            c, _ = Customer.objects.get_or_create(
                user=u,
                defaults={
                    "phone": PHONE_POOL[i % len(PHONE_POOL)],
                    "address": f"Адрес клиента {i+1}",
                    "city": random.choice(["Минск", "Гродно", "Брест"]),
                    "birth_date": birth_dates[i % len(birth_dates)],
                    "preferred_pickup": random.choice(pickup_points),
                },
            )
            customers.append(c)
        return customers

    def _create_employees(self, users):
        roles = ["manager", "warehouse"]
        birth_dates = [date(1992, 7, 7), date(1996, 2, 17)]
        employees = []
        for i, u in enumerate(users):
            e, _ = Employee.objects.get_or_create(
                user=u,
                defaults={
                    "phone": PHONE_POOL[(i + 2) % len(PHONE_POOL)],
                    "role": roles[i % len(roles)],
                    "birth_date": birth_dates[i % len(birth_dates)],
                },
            )
            employees.append(e)
        return employees

    def _create_reviews(self, customer_users):
        for i, u in enumerate(customer_users, start=1):
            Review.objects.get_or_create(
                user=u,
                name=f"Покупатель {i}",
                defaults={
                    "rating": random.randint(3, 5),
                    "text": f"Демо-отзыв №{i}. Всё понравилось.",
                },
            )

    def _create_orders(self, customers, employees, products, promo_codes):
        for customer in customers:
            for _ in range(2):
                promo = random.choice(promo_codes + [None])
                pickup = customer.preferred_pickup

                order = Order.objects.create(
                    customer=customer,
                    employee=random.choice(employees),
                    promo_code=promo if promo and promo.is_valid else None,
                    pickup_point=pickup,
                    status=random.choice(["pending", "processing", "delivered"]),
                    delivery_date=timezone.now() + timedelta(days=random.randint(1, 7)),
                )

                items = random.sample(products, k=random.randint(1, 4))
                for p in items:
                    OrderItem.objects.create(
                        order=order,
                        product=p,
                        quantity=random.randint(1, 5),
                        price_per_unit=p.price,
                    )