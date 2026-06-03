import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
from store.models import (
    Company, CompanyHistory, Article, Glossary, Contact, Vacancy,
    Review, PromoCode, Manufacturer, ProductCategory, Product,
    PickupPoint, Customer, Employee, Order, OrderItem
)

logger = logging.getLogger('store')


class Command(BaseCommand):
    help = 'Seed database with demo data for Variant 10 (Household Chemicals Store)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seeding...')

        # Create superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@chemshop.by', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created superuser: admin / admin123'))

        # Create company info
        if not Company.objects.exists():
            Company.objects.create(
                name='Чистый Дом',
                description='Магазин бытовой химии с широким ассортиментом товаров для дома и сада.',
                email='info@chemshop.by',
                phone='+375 (29) 123-45-67',
                address='г. Минск, пр. Независимости, 100',
                founded_year=2010,
            )
            self.stdout.write('Created company info')

        # Create company history
        history_data = [
            (2010, 'Открытие первого магазина'),
            (2012, 'Запуск интернет-магазина'),
            (2015, 'Открытие второго магазина в Минске'),
            (2018, 'Расширение ассортимента до 5000 товаров'),
            (2020, 'Внедрение системы лояльности'),
            (2022, 'Открытие магазинов в регионах'),
            (2024, 'Запуск мобильной версии сайта'),
            (2026, 'Новая система доставки'),
        ]
        company = Company.objects.first()
        for year, event in history_data:
            CompanyHistory.objects.get_or_create(
                company=company, year=year, defaults={'event': event}
            )
        self.stdout.write('Created company history')

        # Create articles (news)
        articles_data = [
            ('Новое поступление бытовой химии', 'Расширили ассортимент экологичных средств', 'Мы рады сообщить о поступлении новой линейки экологичных средств для уборки дома...'),
            ('Скидки на моющие средства', 'Скидки до 30% наselected товары', 'Только в этом месяце скидки на моющие средства от ведущих производителей...'),
            ('Открытие нового магазина', 'Третий магазин в сети Чистый Дом', 'Приглашаем посетить наш новый магазин по адресу ул. Притыцкого 15...'),
        ]
        for title, summary, content in articles_data:
            Article.objects.get_or_create(
                title=title,
                defaults={'summary': summary, 'content': content, 'is_published': True}
            )
        self.stdout.write('Created 3 articles')

        # Create glossary
        glossary_data = [
            ('Что такое ПАВ?', 'Поверхностно-активные вещества - компоненты моющих средств, отвечающие за очищение...'),
            ('Как хранить бытовую химию?', 'Храните в сухом прохладном месте в оригинальной упаковке...'),
            ('Что такое эко-средства?', 'Средства с биоразлагаемыми компонентами, безопасные для окружающей среды...'),
            ('Как выбрать средство для стирки?', 'Выбирайте исходя из типа ткани, степени загрязнения и наличия аллергии...'),
        ]
        for question, answer in glossary_data:
            Glossary.objects.get_or_create(question=question, defaults={'answer': answer})
        self.stdout.write('Created 4 glossary terms')

        # Create contacts
        contacts_data = [
            ('Иванов', 'Иван', 'Директор магазина', 'Общие вопросы', '+375 (29) 111-22-33', 'ivanov@chemshop.by'),
            ('Петрова', 'Анна', 'Менеджер по продажам', 'Консультации по товарам', '+375 (29) 222-33-44', 'petrova@chemshop.by'),
            ('Сидоров', 'Петр', 'Складской работник', 'Вопросы по наличию', '+375 (29) 333-44-55', 'sidorov@chemshop.by'),
            ('Козлова', 'Елена', 'Бухгалтер', 'Финансовые вопросы', '+375 (29) 444-55-66', 'kozlova@chemshop.by'),
            ('Новиков', 'Андрей', 'Курьер', 'Доставка заказов', '+375 (29) 555-66-77', 'novikov@chemshop.by'),
        ]
        for last, first, position, desc, phone, email in contacts_data:
            Contact.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'position': position,
                    'description': desc,
                    'phone': phone,
                }
            )
        self.stdout.write('Created 5 contacts')

        # Create vacancies
        vacancies_data = [
            ('Продавец-консультант', 'Консультация покупателей, выкладка товара', 2000, 3000),
            ('Складской работник', 'Приёмка и отгрузка товара', 1800, 2500),
            ('Курьер', 'Доставка заказов покупателям', 1500, 2200),
            ('Менеджер по закупкам', 'Работа с поставщиками', 2500, 3500),
        ]
        for title, desc, min_s, max_s in vacancies_data:
            Vacancy.objects.get_or_create(
                title=title,
                defaults={'description': desc, 'salary_min': min_s, 'salary_max': max_s, 'is_active': True}
            )
        self.stdout.write('Created 4 vacancies')

        # Create manufacturers
        manufacturers_data = [
            ('Procter & Gamble', 'США', 'https://www.pg.com'),
            ('Henkel', 'Германия', 'https://www.henkel.com'),
            ('Unilever', 'Великобритания', 'https://www.unilever.com'),
            ('Nevskaya Kosmetika', 'Россия', 'https://www.nevskaya.ru'),
            ('Sarma', 'Беларусь', 'https://www.sarma.by'),
        ]
        manufacturers = {}
        for name, country, website in manufacturers_data:
            m, _ = Manufacturer.objects.get_or_create(name=name, defaults={'country': country, 'website': website})
            manufacturers[name] = m
        self.stdout.write('Created 5 manufacturers')

        # Create product categories
        categories_data = [
            ('Стиральные порошки', 'Средства для стирки белья'),
            ('Средства для мытья посуды', 'Жидкости и гели для посуды'),
            ('Чистящие средства', 'Для кухни, ванной, унитаза'),
            ('Освежители воздуха', 'Аэрозоли и диффузоры'),
            ('Средства для стирки', 'Гели, капсулы, кондиционеры'),
            ('Дезинфицирующие средства', 'Антисептики и дезинфектанты'),
        ]
        categories = {}
        for name, desc in categories_data:
            cat, _ = ProductCategory.objects.get_or_create(name=name, defaults={'description': desc})
            categories[name] = cat
        self.stdout.write('Created 6 categories')

        # Create products (10+ items)
        products_data = [
            ('Tide Автомат', 'Стиральный порошок', 'Стиральные порошки', 15.50, 'pcs', 50, 'Procter & Gamble'),
            ('Ariel Горный родник', 'Стиральный порошок', 'Стиральные порошки', 14.20, 'pcs', 45, 'Procter & Gamble'),
            ('Fairy Original', 'Средство для посуды', 'Средства для мытья посуды', 5.90, 'ml', 100, 'Procter & Gamble'),
            ('AOS Лимон', 'Средство для посуды', 'Средства для мытья посуды', 4.50, 'ml', 80, 'Procter & Gamble'),
            ('Domestos Pine Fresh', 'Чистящее средство', 'Чистящие средства', 7.80, 'ml', 60, 'Unilever'),
            ('Cif Cream', 'Чистящий крем', 'Чистящие средства', 8.50, 'g', 55, 'Unilever'),
            ('Bref Power', 'Для унитаза', 'Чистящие средства', 6.20, 'pcs', 70, 'Henkel'),
            ('Glade Lavender', 'Освежитель воздуха', 'Освежители воздуха', 9.90, 'ml', 40, 'Henkel'),
            ('Lenor Кондиционер', 'Кондиционер для белья', 'Средства для стирки', 11.50, 'ml', 65, 'Procter & Gamble'),
            ('Persil Color', 'Гель для стирки', 'Средства для стирки', 18.90, 'ml', 35, 'Henkel'),
            ('Detox Дезинфектор', 'Дезинфицирующее средство', 'Дезинфицирующие средства', 12.00, 'ml', 50, 'Sarma'),
            ('Sarma Актив', 'Стиральный порошок', 'Стиральные порошки', 10.50, 'pcs', 90, 'Sarma'),
        ]
        products = {}
        for name, desc, cat_name, price, unit, stock, manuf_name in products_data:
            product = Product.objects.create(
                name=name,
                description=desc,
                category=categories[cat_name],
                price=price,
                unit=unit,
                stock_quantity=stock,
                is_available=True,
            )
            product.manufacturers.add(manufacturers[manuf_name])
            products[name] = product
        self.stdout.write(self.style.SUCCESS(f'Created {len(products)} products'))

        # Create pickup points
        pickup_data = [
            ('пр. Независимости, 100', 'Минск', '+375 (29) 100-00-00', 'Пн-Вс 9:00-21:00'),
            ('ул. Притыцкого, 15', 'Минск', '+375 (29) 200-00-00', 'Пн-Вс 10:00-22:00'),
            ('ул. Советская, 50', 'Гомель', '+375 (29) 300-00-00', 'Пн-Сб 9:00-20:00'),
            ('пр. Московский, 25', 'Брест', '+375 (29) 400-00-00', 'Пн-Вс 9:00-21:00'),
        ]
        pickup_points = {}
        for address, city, phone, hours in pickup_data:
            pp, _ = PickupPoint.objects.get_or_create(
                address=address,
                defaults={'city': city, 'phone': phone, 'working_hours': hours}
            )
            pickup_points[city] = pp
        self.stdout.write('Created 4 pickup points')

        # Create customers
        customers_data = [
            ('customer1', 'Смирнов', 'Алексей', 'customer1@mail.by', '+375 (29) 111-22-33', '1990-05-15', 'Минск', 'пр. Независимости 10'),
            ('customer2', 'Кузнецова', 'Мария', 'customer2@mail.by', '+375 (29) 222-33-44', '1985-08-22', 'Гомель', 'ул. Ленина 25'),
            ('customer3', 'Попов', 'Дмитрий', 'customer3@mail.by', '+375 (29) 333-44-55', '1992-12-01', 'Брест', 'ул. Советская 5'),
            ('customer4', 'Васильева', 'Анна', 'customer4@mail.by', '+375 (29) 444-55-66', '1988-03-10', 'Минск', 'ул. Притыцкого 15'),
            ('customer5', 'Михайлов', 'Павел', 'customer5@mail.by', '+375 (29) 555-66-77', '1995-07-20', 'Витебск', 'пр. Московский 30'),
        ]
        customers = {}
        for username, last, first, email, phone, dob, city, address in customers_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, email, 'password123')
                user.first_name = first
                user.last_name = last
                user.save()
                customer = Customer.objects.create(
                    user=user,
                    phone=phone,
                    address=address,
                    city=city,
                    birth_date=dob,
                    preferred_pickup=pickup_points.get(city),
                )
                customers[username] = customer
        self.stdout.write(f'Created {len(customers)} customers')

        # Create employees
        employees_data = [
            ('emp1', 'Иванов', 'Иван', 'emp1@chemshop.by', '+375 (29) 100-11-22', 'manager', '1985-06-15'),
            ('emp2', 'Петрова', 'Анна', 'emp2@chemshop.by', '+375 (29) 200-22-33', 'admin_role', '1990-03-20'),
            ('emp3', 'Сидоров', 'Петр', 'emp3@chemshop.by', '+375 (29) 300-33-44', 'warehouse', '1988-11-10'),
        ]
        employees = {}
        for username, last, first, email, phone, role, dob in employees_data:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username, email, 'password123')
                user.first_name = first
                user.last_name = last
                user.save()
                employee = Employee.objects.create(
                    user=user,
                    phone=phone,
                    role=role,
                    birth_date=dob,
                )
                employees[username] = employee
        self.stdout.write(f'Created {len(employees)} employees')

        # Create orders
        product_list = list(Product.objects.all()[:5])
        for cust_key, customer in customers.items():
            order = Order.objects.create(
                customer=customer,
                employee=employees.get('emp1'),
                status='delivered' if cust_key != 'customer5' else 'pending',
                pickup_point=pickup_points.get(customer.city),
            )
            # Add order items
            for i, product in enumerate(product_list[:3]):
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=i + 1,
                    price_per_unit=product.price,
                )
        self.stdout.write(f'Created {len(customers)} orders')

        # Create promo codes
        promo_data = [
            ('WELCOME10', 'Приветственная скидка', 10, '2026-01-01', '2027-12-31', True),
            ('SUMMER2026', 'Летняя акция', 15, '2026-06-01', '2026-08-31', True),
            ('CLEAN20', 'Скидка на чистящие средства', 20, '2026-01-01', '2026-12-31', True),
            ('NEWYEAR', 'Новогодняя скидка', 25, '2026-12-01', '2027-01-15', True),
        ]
        for code, desc, discount, valid_from, valid_to, is_active in promo_data:
            PromoCode.objects.get_or_create(
                code=code,
                defaults={
                    'description': desc,
                    'discount_percent': discount,
                    'valid_from': valid_from,
                    'valid_to': valid_to,
                    'is_active': is_active,
                }
            )
        self.stdout.write('Created 4 promo codes')

        # Create reviews
        reviews_data = [
            ('customer1', 5, 'Отличный магазин! Быстрая доставка и качественный товар.'),
            ('customer2', 4, 'Хороший ассортимент, цены средние.'),
            ('customer3', 5, 'Всегда свежие товары и вежливый персонал.'),
            ('customer4', 4, 'Удобный сайт, легко заказать.'),
        ]
        for cust_key, rating, text in reviews_data:
            customer = customers.get(cust_key)
            if customer:
                Review.objects.create(
                    user=customer.user,
                    name=f'{customer.user.first_name} {customer.user.last_name}',
                    rating=rating,
                    text=text,
                )
        self.stdout.write('Created 4 reviews')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeding completed successfully!'))
        self.stdout.write(self.style.WARNING('\n⚠️ Login credentials:'))
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Customers: customer1-5 / password123')
        self.stdout.write('  Employees: emp1-3 / password123')
