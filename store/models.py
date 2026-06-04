from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from datetime import date


class Company(models.Model):
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    logo = models.ImageField('Логотип', upload_to='company/', blank=True, null=True)
    video_url = models.URLField('Видео', blank=True, null=True)
    founded_year = models.IntegerField('Год основания', blank=True, null=True)
    email = models.EmailField('Email', blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    address = models.TextField('Адрес', blank=True)

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компания'

    def __str__(self):
        return self.name


class CompanyHistory(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE,
                                related_name='history', verbose_name='Компания')
    year = models.IntegerField('Год')
    event = models.TextField('Событие')

    class Meta:
        verbose_name = 'История'
        verbose_name_plural = 'История компании'
        ordering = ['year']

    def __str__(self):
        return f"{self.year}: {self.event[:50]}"


class Article(models.Model):
    title = models.CharField('Заголовок', max_length=300)
    summary = models.CharField('Краткое содержание', max_length=500)
    content = models.TextField('Полное содержание')
    image = models.ImageField('Картинка', upload_to='articles/', blank=True, null=True)
    published_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    updated_date = models.DateTimeField('Дата обновления', auto_now=True)
    is_published = models.BooleanField('Опубликовано', default=True)

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-published_date']

    def __str__(self):
        return self.title


class Glossary(models.Model):
    question = models.CharField('Вопрос/Термин', max_length=300)
    answer = models.TextField('Ответ/Определение')
    added_date = models.DateField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Термин'
        verbose_name_plural = 'Словарь терминов'
        ordering = ['question']

    def __str__(self):
        return self.question


class Contact(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+375 \(2[59]\) \d{3}-\d{2}-\d{2}$',
        message='Формат: +375 (29) XXX-XX-XX'
    )
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    position = models.CharField('Должность', max_length=200)
    description = models.TextField('Описание работы')
    phone = models.CharField('Телефон', validators=[phone_regex], max_length=20)
    email = models.EmailField('Email')
    photo = models.ImageField('Фото', upload_to='contacts/', blank=True, null=True)

    class Meta:
        verbose_name = 'Контакт'
        verbose_name_plural = 'Контакты'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Vacancy(models.Model):
    title = models.CharField('Должность', max_length=200)
    description = models.TextField('Описание')
    salary_min = models.DecimalField('Зарплата от', max_digits=10,
                                     decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField('Зарплата до', max_digits=10,
                                     decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField('Активна', default=True)
    created_date = models.DateField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'

    def __str__(self):
        return self.title


class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             verbose_name='Пользователь', null=True, blank=True)
    name = models.CharField('Имя', max_length=100)
    rating = models.IntegerField('Оценка', choices=RATING_CHOICES)
    text = models.TextField('Текст отзыва')
    date = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    is_approved = models.BooleanField('Одобрен', default=False)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-date']

    def __str__(self):
        return f"Отзыв от {self.name} — {self.rating}⭐"


class PromoCode(models.Model):
    code = models.CharField('Код', max_length=50, unique=True)
    description = models.TextField('Описание')
    discount_percent = models.IntegerField(
        'Скидка %',
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    valid_from = models.DateField('Действует с')
    valid_to = models.DateField('Действует до')
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды и купоны'

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        today = date.today()
        return self.is_active and self.valid_from <= today <= self.valid_to


class Manufacturer(models.Model):
    name = models.CharField('Название', max_length=200)
    country = models.CharField('Страна', max_length=100)
    website = models.URLField('Сайт', blank=True, null=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Изготовитель'
        verbose_name_plural = 'Изготовители'

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = [
        ('pcs', 'Штуки'),
        ('kg', 'Килограммы'),
        ('l', 'Литры'),
        ('g', 'Граммы'),
        ('ml', 'Миллилитры'),
    ]
    name = models.CharField('Название', max_length=300)
    # Один ко многим: категория → много товаров
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL,
                                 null=True, verbose_name='Категория',
                                 related_name='products')
    # Многие ко многим: товар ↔ изготовители
    manufacturers = models.ManyToManyField(Manufacturer, verbose_name='Изготовители',
                                           related_name='products')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    unit = models.CharField('Единица измерения', max_length=10,
                            choices=UNIT_CHOICES, default='pcs')
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='products/', blank=True, null=True)
    stock_quantity = models.IntegerField('Количество на складе', default=0)
    is_available = models.BooleanField('Доступен', default=True)
    created_date = models.DateTimeField('Дата добавления', auto_now_add=True)
    updated_date = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']

    def __str__(self):
        return self.name


class PickupPoint(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+375 \(2[59]\) \d{3}-\d{2}-\d{2}$',
        message='Формат: +375 (29) XXX-XX-XX'
    )
    address = models.CharField('Адрес', max_length=300)
    city = models.CharField('Город', max_length=100)
    phone = models.CharField('Телефон', validators=[phone_regex], max_length=20)
    working_hours = models.CharField('Часы работы', max_length=100)

    class Meta:
        verbose_name = 'Точка самовывоза'
        verbose_name_plural = 'Точки самовывоза'

    def __str__(self):
        return f"{self.city}, {self.address}"


class Customer(models.Model):
    # Один к одному: User ↔ Customer
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                verbose_name='Пользователь',
                                related_name='customer_profile')
    phone_regex = RegexValidator(
        regex=r'^\+375 \(2[59]\) \d{3}-\d{2}-\d{2}$',
        message='Формат: +375 (29) XXX-XX-XX'
    )
    phone = models.CharField('Телефон', validators=[phone_regex],
                             max_length=20, blank=True)
    address = models.TextField('Адрес', blank=True)
    city = models.CharField('Город', max_length=100, blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    preferred_pickup = models.ForeignKey(PickupPoint, on_delete=models.SET_NULL,
                                         null=True, blank=True,
                                         verbose_name='Предпочтительная точка самовывоза')

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None

    def is_adult(self):
        age = self.age
        return age is not None and age >= 18


class Employee(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Менеджер'),
        ('warehouse', 'Складской работник'),
        ('courier', 'Курьер'),
        ('admin_role', 'Администратор'),
    ]
    # Один к одному: User ↔ Employee
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                verbose_name='Пользователь',
                                related_name='employee_profile')
    phone_regex = RegexValidator(
        regex=r'^\+375 \(2[59]\) \d{3}-\d{2}-\d{2}$',
        message='Формат: +375 (29) XXX-XX-XX'
    )
    phone = models.CharField('Телефон', validators=[phone_regex], max_length=20)
    role = models.CharField('Роль', max_length=20,
                            choices=ROLE_CHOICES, default='manager')
    birth_date = models.DateField('Дата рождения')
    hire_date = models.DateField('Дата найма', auto_now_add=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        name = self.user.get_full_name() or self.user.username
        return f"{name} ({self.get_role_display()})"

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    def is_adult(self):
        return self.age >= 18


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    # Один ко многим: клиент → много заказов
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE,
                                 verbose_name='Клиент', related_name='orders')
    # Один ко многим: сотрудник → много заказов
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL,
                                 null=True, blank=True,
                                 verbose_name='Сотрудник', related_name='orders')
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL,
                                   null=True, blank=True, verbose_name='Промокод')
    pickup_point = models.ForeignKey(PickupPoint, on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     verbose_name='Точка самовывоза')
    status = models.CharField('Статус', max_length=20,
                              choices=STATUS_CHOICES, default='pending')
    sale_date = models.DateTimeField('Дата продажи', auto_now_add=True)
    delivery_date = models.DateTimeField('Дата доставки', null=True, blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-sale_date']

    def __str__(self):
        return f"Заказ #{self.pk} от {self.customer}"

    @property
    def total_price(self):
        total = sum(
            item.quantity * item.price_per_unit
            for item in self.order_items.all()
        )
        if self.promo_code and self.promo_code.is_valid:
            total = total * (1 - self.promo_code.discount_percent / 100)
        return round(total, 2)


class OrderItem(models.Model):
    # Связующая таблица Order ↔ Product (ManyToMany через промежуточную модель)
    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='order_items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name='Товар')
    quantity = models.IntegerField('Количество', validators=[MinValueValidator(1)])
    price_per_unit = models.DecimalField('Цена за единицу',
                                         max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.price_per_unit