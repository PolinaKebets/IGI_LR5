import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta, datetime
from store.models import (
    Company, CompanyHistory, Article, Glossary, Contact, Vacancy,
    Review, PromoCode, Manufacturer, ProductCategory, Product,
    PickupPoint, Customer, Employee, Order, OrderItem
)
from store.forms import ReviewForm, CustomerProfileForm, OrderForm, LoginForm, RegisterForm


@pytest.mark.django_db
class TestModels:
    """Test model creation and methods"""

    def test_company_creation(self):
        company = Company.objects.create(
            name='Test Company',
            description='Test description',
            email='test@test.com',
            phone='+375 (29) 123-45-67',
        )
        assert str(company) == 'Test Company'

    def test_company_history_creation(self):
        company = Company.objects.create(name='Test')
        history = CompanyHistory.objects.create(
            company=company,
            year=2020,
            event='Test event'
        )
        assert '2020' in str(history)

    def test_article_creation(self):
        article = Article.objects.create(
            title='Test Article',
            summary='Test summary',
            content='Test content',
        )
        assert str(article) == 'Test Article'
        assert article.is_published is True

    def test_glossary_creation(self):
        glossary = Glossary.objects.create(
            question='Test question?',
            answer='Test answer'
        )
        assert str(glossary) == 'Test question?'

    def test_contact_creation(self):
        contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            position='Manager',
            description='Test',
            phone='+375 (29) 123-45-67',
            email='john@test.com'
        )
        assert 'Doe' in str(contact)

    def test_vacancy_creation(self):
        vacancy = Vacancy.objects.create(
            title='Developer',
            description='Test job',
            salary_min=1000,
            salary_max=2000,
        )
        assert str(vacancy) == 'Developer'
        assert vacancy.is_active is True

    def test_review_creation(self):
        user = User.objects.create_user('testuser', 'test@test.com', 'password')
        review = Review.objects.create(
            user=user,
            name='Test User',
            rating=5,
            text='Great!'
        )
        assert review.rating == 5
        assert '5' in str(review)

    def test_promocode_creation(self):
        promo = PromoCode.objects.create(
            code='TEST10',
            description='Test discount',
            discount_percent=10,
            valid_from=date.today() - timedelta(days=1),
            valid_to=date.today() + timedelta(days=30),
        )
        assert str(promo) == 'TEST10'
        assert promo.is_valid is True

    def test_promocode_expired(self):
        promo = PromoCode.objects.create(
            code='EXPIRED',
            discount_percent=5,
            valid_from=date.today() - timedelta(days=30),
            valid_to=date.today() - timedelta(days=1),
        )
        assert promo.is_valid is False

    def test_manufacturer_creation(self):
        manufacturer = Manufacturer.objects.create(
            name='Test Manufacturer',
            country='Belarus',
        )
        assert str(manufacturer) == 'Test Manufacturer'

    def test_category_creation(self):
        category = ProductCategory.objects.create(
            name='Test Category',
        )
        assert str(category) == 'Test Category'

    def test_product_creation(self):
        category = ProductCategory.objects.create(name='Test')
        product = Product.objects.create(
            name='Test Product',
            category=category,
            price=10.50,
            unit='pcs',
            stock_quantity=100,
        )
        assert str(product) == 'Test Product'
        assert product.is_available is True

    def test_product_many_to_many(self):
        category = ProductCategory.objects.create(name='Test')
        manufacturer = Manufacturer.objects.create(name='Test Mfg')
        product = Product.objects.create(
            name='Test Product',
            category=category,
            price=10.50,
        )
        product.manufacturers.add(manufacturer)
        assert manufacturer in product.manufacturers.all()

    def test_pickup_point_creation(self):
        pickup = PickupPoint.objects.create(
            address='Test St, 10',
            city='Minsk',
            phone='+375 (29) 123-45-67',
            working_hours='9:00-21:00'
        )
        assert 'Minsk' in str(pickup)

    def test_customer_creation(self):
        user = User.objects.create_user('customer', 'c@test.com', 'password')
        customer = Customer.objects.create(
            user=user,
            phone='+375 (29) 123-45-67',
            city='Minsk',
            birth_date=date(1990, 1, 1)
        )
        assert customer.age >= 18
        assert customer.is_adult() is True

    def test_customer_underage(self):
        user = User.objects.create_user('young', 'y@test.com', 'password')
        customer = Customer(
            user=user,
            birth_date=date.today() - timedelta(days=365*10)
        )
        assert customer.age < 18
        assert customer.is_adult() is False

    def test_employee_creation(self):
        user = User.objects.create_user('employee', 'e@test.com', 'password')
        employee = Employee.objects.create(
            user=user,
            phone='+375 (29) 123-45-67',
            role='manager',
            birth_date=date(1990, 1, 1)
        )
        assert employee.is_adult() is True
        assert 'Менеджер' in str(employee) or 'manager' in str(employee).lower()

    def test_order_creation(self):
        user = User.objects.create_user('customer', 'c@test.com', 'password')
        customer = Customer.objects.create(
            user=user,
            birth_date=date(1990, 1, 1)
        )
        order = Order.objects.create(
            customer=customer,
            status='pending'
        )
        assert 'Заказ' in str(order)
        assert order.total_price == 0

    def test_order_with_items(self):
        user = User.objects.create_user('customer', 'c@test.com', 'password')
        customer = Customer.objects.create(user=user, birth_date=date(1990, 1, 1))
        category = ProductCategory.objects.create(name='Test')
        product = Product.objects.create(name='Product', category=category, price=10.00)
        
        order = Order.objects.create(customer=customer, status='pending')
        OrderItem.objects.create(order=order, product=product, quantity=2, price_per_unit=10.00)
        
        assert order.total_price == 20.00

    def test_orderitem_subtotal(self):
        user = User.objects.create_user('customer', 'c@test.com', 'password')
        customer = Customer.objects.create(user=user, birth_date=date(1990, 1, 1))
        category = ProductCategory.objects.create(name='Test')
        product = Product.objects.create(name='Product', category=category, price=15.00)
        
        order = Order.objects.create(customer=customer)
        item = OrderItem.objects.create(order=order, product=product, quantity=3, price_per_unit=15.00)
        
        assert item.subtotal == 45.00


@pytest.mark.django_db
class TestViews:
    """Test views"""

    def test_home_view(self, client):
        response = client.get(reverse('store:home'))
        assert response.status_code == 200

    def test_about_view(self, client):
        response = client.get(reverse('store:about'))
        assert response.status_code == 200

    def test_news_list_view(self, client):
        response = client.get(reverse('store:news'))
        assert response.status_code == 200

    def test_glossary_view(self, client):
        response = client.get(reverse('store:glossary'))
        assert response.status_code == 200

    def test_contacts_view(self, client):
        response = client.get(reverse('store:contacts'))
        assert response.status_code == 200

    def test_vacancies_view(self, client):
        response = client.get(reverse('store:vacancies'))
        assert response.status_code == 200

    def test_privacy_view(self, client):
        response = client.get(reverse('store:privacy'))
        assert response.status_code == 200

    def test_calendar_view(self, client):
        response = client.get(reverse('store:calendar'))
        assert response.status_code == 200

    def test_product_list_view(self, client):
        response = client.get(reverse('store:product_list'))
        assert response.status_code == 200

    def test_reviews_view(self, client):
        response = client.get(reverse('store:reviews'))
        assert response.status_code == 200

    def test_promocodes_view(self, client):
        response = client.get(reverse('store:promo_codes'))
        assert response.status_code == 200

    def test_login_view(self, client):
        response = client.get(reverse('store:login'))
        assert response.status_code == 200

    def test_register_view(self, client):
        response = client.get(reverse('store:register'))
        assert response.status_code == 200

    def test_statistics_requires_superuser(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        response = client.get(reverse('store:statistics'))
        assert response.status_code == 302

    def test_statistics_superuser_access(self, client):
        user = User.objects.create_superuser(username='admin', password='password')
        client.force_login(user)
        response = client.get(reverse('store:statistics'))
        assert response.status_code == 200

    def test_profile_requires_login(self, client):
        response = client.get(reverse('store:profile'))
        assert response.status_code == 302

    def test_order_list_requires_login(self, client):
        response = client.get(reverse('store:order_list'))
        assert response.status_code == 302

    def test_review_add_requires_login(self, client):
        response = client.get(reverse('store:add_review'))
        assert response.status_code == 302


@pytest.mark.django_db
class TestForms:
    """Test forms"""

    def test_review_form_valid(self):
        form = ReviewForm(data={
            'name': 'Test User',
            'rating': 5,
            'text': 'Great product!'
        })
        assert form.is_valid()

    def test_review_form_invalid_rating(self):
        form = ReviewForm(data={
            'name': 'Test',
            'rating': 10,  # Invalid
            'text': 'Test'
        })
        assert not form.is_valid()
        assert 'rating' in form.errors

    def test_register_form_valid(self):
        form = RegisterForm(data={
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        assert form.is_valid()

    def test_login_form_valid(self):
        User.objects.create_user(username='testuser', password='password')
        form = LoginForm(data={'username': 'testuser', 'password': 'password'})
        assert form.is_valid()

    def test_login_form_invalid(self):
        form = LoginForm(data={'username': 'wrong', 'password': 'wrong'})
        assert not form.is_valid()


@pytest.mark.django_db
class TestProductFilters:
    """Test product filtering and search"""

    def test_product_search(self, client):
        category = ProductCategory.objects.create(name='Test')
        Product.objects.create(name='Test Product', category=category, price=10.00)
        Product.objects.create(name='Other Product', category=category, price=20.00)
        
        response = client.get(reverse('store:product_list'), {'q': 'Test'})
        assert response.status_code == 200
        assert len(response.context['products']) == 1

    def test_product_filter_by_price(self, client):
        category = ProductCategory.objects.create(name='Test')
        Product.objects.create(name='Cheap', category=category, price=5.00)
        Product.objects.create(name='Expensive', category=category, price=50.00)
        
        response = client.get(reverse('store:product_list'), {'min_price': 10, 'max_price': 100})
        assert response.status_code == 200
        assert len(response.context['products']) == 1

    def test_product_sort(self, client):
        category = ProductCategory.objects.create(name='Test')
        Product.objects.create(name='Product A', category=category, price=30.00)
        Product.objects.create(name='Product B', category=category, price=10.00)
        
        response = client.get(reverse('store:product_list'), {'sort': 'price'})
        assert response.status_code == 200


@pytest.mark.django_db
class TestAPI:
    """Test API endpoints"""

    def test_api_currency_rates(self, client):
        response = client.get(reverse('store:api_currency_rates'))
        assert response.status_code == 200
        data = response.json()
        assert 'rates' in data

    def test_api_statistics_unauthorized(self, client):
        response = client.get(reverse('store:api_statistics'))
        assert response.status_code == 401

    def test_api_statistics_authorized(self, client):
        user = User.objects.create_superuser(username='admin', password='password')
        client.force_login(user)
        response = client.get(reverse('store:api_statistics'))
        assert response.status_code == 200
        data = response.json()
        assert 'total_products' in data


@pytest.mark.django_db
class TestAuthViews:
    """Test authentication views"""

    def test_login_success(self, client):
        User.objects.create_user(username='testuser', password='password')
        response = client.post(reverse('store:login'), {
            'username': 'testuser',
            'password': 'password'
        })
        assert response.status_code == 302

    def test_login_failure(self, client):
        response = client.post(reverse('store:login'), {
            'username': 'wrong',
            'password': 'wrong'
        })
        assert response.status_code == 200

    def test_logout(self, client):
        user = User.objects.create_user(username='testuser', password='password')
        client.force_login(user)
        response = client.post(reverse('store:logout'))
        assert response.status_code == 302

    def test_register_success(self, client):
        response = client.post(reverse('store:register'), {
            'username': 'newuser',
            'email': 'new@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'TestPass123!',
            'password2': 'TestPass123!',
        })
        assert response.status_code == 302


@pytest.mark.django_db
class TestEmployeeDashboard:
    """Test employee dashboard"""

    def test_employee_dashboard_requires_employee(self, client):
        user = User.objects.create_user(username='user', password='password')
        client.force_login(user)
        response = client.get(reverse('store:employee_dashboard'))
        assert response.status_code == 302

    def test_employee_dashboard_success(self, client):
        user = User.objects.create_user(username='emp', password='password', email='emp@test.com')
        Employee.objects.create(
            user=user,
            phone='+375 (29) 123-45-67',
            role='manager',
            birth_date=date(1990, 1, 1)
        )
        client.force_login(user)
        response = client.get(reverse('store:employee_dashboard'))
        assert response.status_code == 200


@pytest.mark.django_db
class TestOrderCRUD:
    """Test order CRUD operations"""

    def test_order_list_empty(self, client):
        user = User.objects.create_user(username='customer', password='password')
        Customer.objects.create(user=user, birth_date=date(1990, 1, 1))
        client.force_login(user)
        response = client.get(reverse('store:order_list'))
        assert response.status_code == 200

    def test_order_create_requires_customer(self, client):
        user = User.objects.create_user(username='user', password='password')
        client.force_login(user)
        response = client.get(reverse('store:order_create'))
        assert response.status_code == 302  # Redirects to profile

    def test_order_detail_requires_permission(self, client):
        user1 = User.objects.create_user(username='customer1', password='password')
        user2 = User.objects.create_user(username='customer2', password='password')
        c1 = Customer.objects.create(user=user1, birth_date=date(1990, 1, 1))
        Customer.objects.create(user=user2, birth_date=date(1990, 1, 1))
        
        order = Order.objects.create(customer=c1)
        client.force_login(user2)
        
        response = client.get(reverse('store:order_detail', kwargs={'pk': order.pk}))
        assert response.status_code == 302  # Access denied


@pytest.mark.django_db
class TestExternalAPI:
    """Test external API helpers"""

    def test_get_currency_rates(self):
        from store.views import get_currency_rates
        rates = get_currency_rates()
        assert isinstance(rates, dict)
        assert 'BYN' in rates

    def test_get_product_safety_info(self):
        from store.views import get_product_safety_info
        tip = get_product_safety_info('Test')
        assert isinstance(tip, str)
        assert len(tip) > 0
