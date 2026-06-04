import logging
import json
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Sum, F, DecimalField, Count, Avg, Q
from django.db.models.functions import TruncMonth, ExtractYear
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.views.decorators.http import require_POST
from calendar import TextCalendar
from datetime import date, timedelta
from .models import (
    Company, CompanyHistory, Article, Glossary, Contact, Vacancy,
    Review, PromoCode, Manufacturer, ProductCategory, Product,
    PickupPoint, Customer, Employee, Order, OrderItem
)
from .forms import ReviewForm, CustomerProfileForm, OrderForm, LoginForm, RegisterForm, ProductFilterForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm


# Существующая функция для списка отзывов
def reviews(request):
    reviews_list = Review.objects.filter(is_approved=True).order_by('-created_at')
    return render(request, 'store/reviews.html', {'reviews': reviews_list})


# Добавление отзыва
@login_required
def add_review(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.is_approved = False  # Требует модерации
            review.save()
            messages.success(request, 'Ваш отзыв отправлен на модерацию!')
            return redirect('store:reviews')
    else:
        form = ReviewForm()
    return render(request, 'store/add_review.html', {'form': form})


# 🆕 Редактирование отзыва
@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Проверка: только автор отзыва может редактировать
    if review.user != request.user:
        messages.error(request, 'Вы не можете редактировать чужой отзыв!')
        return redirect('store:reviews')

    # Нельзя редактировать уже одобренный отзыв
    if review.is_approved:
        messages.warning(request, 'Одобренный отзыв нельзя редактировать. Создайте новый отзыв.')
        return redirect('store:reviews')

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш отзыв обновлён!')
            return redirect('store:reviews')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'store/edit_review.html', {
        'form': form,
        'review': review
    })


# 🆕 Удаление отзыва
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # Проверка: только автор или админ может удалить
    if review.user != request.user and not request.user.is_superuser:
        messages.error(request, 'Вы не можете удалить чужой отзыв!')
        return redirect('store:reviews')

    if request.method == 'POST':
        review.delete()
        messages.success(request, 'Отзыв удалён!')
        return redirect('store:reviews')

    return render(request, 'store/confirm_delete_review.html', {'review': review})


logger = logging.getLogger('store')


# External API helpers
def get_currency_rates():
    """Get currency rates from external API (exchangerate-api.com)"""
    try:
        response = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('rates', {})
    except Exception as e:
        logger.error(f'Error fetching currency rates: {e}')
    return {'BYN': 3.26, 'EUR': 0.92, 'RUB': 90.5, 'USD': 1.0}


def get_product_safety_info(product_name):
    """Get chemical safety information (simulated external API)"""
    safety_tips = [
        "Храните в недоступном для детей месте",
        "Избегайте контакта с глазами",
        "Используйте перчатки при работе",
        "Храните в сухом прохладном месте",
        "Не смешивайте с другими химическими веществами",
        "При попадании на кожу промойте водой",
        "Беречь от прямых солнечных лучей",
        "Используйте в хорошо проветриваемом помещении",
    ]
    import random
    return random.choice(safety_tips)


# Main pages
def home(request):
    """Home page - shows latest article"""
    last_article = Article.objects.filter(is_published=True).order_by('-published_date').first()
    currency_rates = get_currency_rates()
    safety_tip = get_product_safety_info('')
    
    context = {
        'last_article': last_article,
        'currency_rates': currency_rates,
        'safety_tip': safety_tip,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    logger.info('Home page accessed')
    return render(request, 'store/home.html', context)


def about(request):
    """About company page"""
    company = Company.objects.first()
    history = company.history.all() if company else []
    context = {
        'company': company,
        'history': history,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/about.html', context)


def news_list(request):
    """News list - articles"""
    articles = Article.objects.filter(is_published=True).order_by('-published_date')[:10]
    context = {
        'articles': articles,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/news_list.html', context)


def news_detail(request, pk):
    """News detail page"""
    article = get_object_or_404(Article, pk=pk, is_published=True)
    context = {
        'article': article,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/news_detail.html', context)


def glossary_list(request):
    """Glossary/FAQ page"""
    items = Glossary.objects.all().order_by('question')
    context = {
        'items': items,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/glossary.html', context)


def contacts(request):
    """Contacts page"""
    people = Contact.objects.all()
    context = {
        'people': people,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/contacts.html', context)


def vacancies(request):
    """Vacancies page"""
    items = Vacancy.objects.filter(is_active=True).order_by('-created_date')
    context = {
        'items': items,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/vacancies.html', context)


def privacy(request):
    """Privacy policy page"""
    context = {
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/privacy.html', context)


def calendar_view(request):
    """Calendar view with visual month grid and pickup points working hours"""
    from datetime import timedelta
    from store.models import PickupPoint
    
    now = timezone.now()
    
    # Получаем первый и последний день месяца
    first_day = now.replace(day=1)
    if now.month == 12:
        last_day = now.replace(year=now.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = now.replace(month=now.month + 1, day=1) - timedelta(days=1)
    
    # Создаём календарь: список недель, каждая неделя - список дней
    calendar_weeks = []
    first_weekday = first_day.weekday()  # 0 = понедельник
    current_day = 1
    
    # Предыдущий месяц (серые дни)
    prev_month_last_day = (first_day - timedelta(days=1)).day
    first_week = []
    for i in range(first_weekday):
        first_week.append({'day': prev_month_last_day - first_weekday + i + 1, 'current_month': False})
    
    # Текущий месяц
    week = first_week
    while current_day <= last_day.day:
        if len(week) >= 7:
            calendar_weeks.append(week)
            week = []
        week.append({'day': current_day, 'current_month': True, 'is_today': current_day == now.day})
        current_day += 1
    
    # Следующий месяц (серые дни)
    while len(week) < 7:
        week.append({'day': len(week) - last_day.weekday(), 'current_month': False})
    
    if week:
        calendar_weeks.append(week)
    
    # Получаем график работы пунктов выдачи
    pickup_points = PickupPoint.objects.all().order_by('city', 'address')
    
    # Дни недели
    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    
    context = {
        'calendar_weeks': calendar_weeks,
        'weekdays': weekdays,
        'current_month': now.strftime('%B %Y'),
        'current_month_num': now.month,
        'current_year': now.year,
        'current_time_utc': now,
        'current_time_local': timezone.localtime(),
        'pickup_points': pickup_points,
    }
    return render(request, 'store/calendar.html', context)


# Product views
def product_list(request):
    """Product list with search, filter, sort"""
    qs = Product.objects.filter(is_available=True).select_related('category').prefetch_related('manufacturers')

    # Search
    q = request.GET.get('q')
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        qs = qs.filter(category_id=category_id)

    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            qs = qs.filter(price__gte=float(min_price))
        except (ValueError, TypeError):
            pass
    if max_price:
        try:
            qs = qs.filter(price__lte=float(max_price))
        except (ValueError, TypeError):
            pass

    # Sort
    sort = request.GET.get('sort', 'name')
    if sort in ('name', '-name', 'price', '-price', 'created_date', '-created_date'):
        qs = qs.order_by(sort)

    # Pagination: 12 products per page
    paginator = Paginator(qs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Build form with category choices
    categories = ProductCategory.objects.all().order_by('name')
    category_choices = [('', 'Все категории')] + [(cat.id, cat.name) for cat in categories]
    
    form = ProductFilterForm(request.GET or None)
    form.fields['category'].choices = category_choices

    context = {
        'products': page_obj,
        'categories': categories,
        'form': form,
        'current_sort': sort,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, pk):
    """Product detail page"""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('manufacturers'),
        pk=pk
    )
    safety_tip = get_product_safety_info(product.name)
    
    context = {
        'product': product,
        'safety_tip': safety_tip,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/product_detail.html', context)


# Review views
def reviews_list(request):
    """Reviews list"""
    items = Review.objects.all().order_by('-date')[:20]
    context = {
        'items': items,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/reviews.html', context)


@login_required
def review_add(request):
    """Add review"""
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            if not obj.name:
                obj.name = request.user.get_username()
            obj.save()
            logger.info(f'Review created by {request.user.username}')
            messages.success(request, 'Отзыв добавлен успешно')
            return redirect('store:reviews')
    else:
        form = ReviewForm(initial={'name': request.user.get_username()})
    
    return render(request, 'store/review_add.html', {'form': form})


# PromoCode views
def promocodes(request):
    """Promo codes list"""
    today = timezone.localdate()
    active = PromoCode.objects.filter(is_active=True, valid_from__lte=today, valid_to__gte=today)
    archive = PromoCode.objects.exclude(pk__in=active.values_list('pk', flat=True))
    context = {
        'active': active,
        'archive': archive,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/promocodes.html', context)


# Order views (CRUD - Create, Read, Update, Delete)
@login_required
def order_list(request):
    """READ - Order list for current customer"""
    try:
        customer = request.user.customer_profile
        orders = Order.objects.filter(customer=customer).select_related(
            'pickup_point', 'promo_code'
        ).prefetch_related('order_items__product').order_by('-sale_date')
    except Customer.DoesNotExist:
        orders = []
        messages.warning(request, 'Сначала заполните профиль покупателя')
        return redirect('store:profile')
    
    context = {
        'orders': orders,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/order_list.html', context)


@login_required
def order_detail(request, pk):
    """READ - Order detail page"""
    order = get_object_or_404(Order, pk=pk)
    # Check permission
    if not request.user.is_superuser and order.customer.user != request.user:
        messages.error(request, 'Доступ запрещён')
        return redirect('store:order_list')
    
    context = {
        'order': order,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/order_detail.html', context)


@login_required
def order_create(request):
    """CREATE - Create new order"""
    try:
        customer = request.user.customer_profile
    except Customer.DoesNotExist:
        messages.warning(request, 'Сначала заполните профиль покупателя')
        return redirect('store:profile')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.status = 'pending'
            order.save()
            
            # Add order items from session cart (simplified - direct from POST)
            product_ids = request.POST.getlist('product_ids')
            quantities = request.POST.getlist('quantities')
            
            for pid, qty in zip(product_ids, quantities):
                if qty and int(qty) > 0:
                    product = get_object_or_404(Product, pk=pid)
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=int(qty),
                        price_per_unit=product.price
                    )
            
            logger.info(f'Order #{order.id} created by {request.user.username}')
            messages.success(request, 'Заказ создан успешно')
            return redirect('store:order_detail', pk=order.pk)
    else:
        form = OrderForm()
    
    products = Product.objects.filter(is_available=True)[:10]
    pickup_points = PickupPoint.objects.all()
    
    context = {
        'form': form,
        'products': products,
        'pickup_points': pickup_points,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/order_create.html', context)


@login_required
def order_update(request, pk):
    """UPDATE - Update order (change status, pickup point)"""
    order = get_object_or_404(Order, pk=pk)
    
    # Check permission - only employee or superuser can update
    if not request.user.is_superuser:
        try:
            employee = request.user.employee_profile
        except Employee.DoesNotExist:
            messages.error(request, 'Доступ запрещён')
            return redirect('store:order_list')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            logger.info(f'Order #{order.id} status updated to {new_status}')
            messages.success(request, 'Статус заказа обновлён')
            return redirect('store:order_detail', pk=order.pk)
    
    context = {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/order_update.html', context)


@login_required
@require_POST
def order_delete(request, pk):
    """DELETE - Cancel/delete order"""
    order = get_object_or_404(Order, pk=pk)
    
    # Check permission
    if order.customer.user == request.user or request.user.is_superuser:
        if order.status not in ('delivered', 'shipped'):
            order.delete()
            logger.info(f'Order #{order.id} deleted by {request.user.username}')
            messages.success(request, 'Заказ удалён')
        else:
            messages.error(request, 'Нельзя удалить отправленный или доставленный заказ')
    else:
        messages.error(request, 'Доступ запрещён')
    
    return redirect('store:order_list')


@login_required
@require_POST
def order_cancel(request, pk):
    """Cancel order (alternative to delete)"""
    order = get_object_or_404(Order, pk=pk)
    if order.customer.user == request.user or request.user.is_superuser:
        if order.status not in ('delivered', 'cancelled'):
            order.status = 'cancelled'
            order.save()
            logger.info(f'Order #{order.id} cancelled by {request.user.username}')
            messages.success(request, 'Заказ отменён')
        else:
            messages.warning(request, 'Нельзя отменить этот заказ')
    else:
        messages.error(request, 'Доступ запрещён')
    
    return redirect('store:order_list')


# Employee views
@login_required
def employee_dashboard(request):
    """Employee dashboard"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'Вы не являетесь сотрудником')
        return redirect('store:home')
    
    # Orders handled by this employee
    orders = Order.objects.filter(employee=employee).order_by('-sale_date')[:10]
    
    context = {
        'employee': employee,
        'orders': orders,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/employee_dashboard.html', context)


# Statistics view
@user_passes_test(lambda u: u.is_superuser)
def statistics(request):
    """Statistics dashboard"""
    # Top product by quantity sold
    top_product = (
        OrderItem.objects.values('product__id', 'product__name')
        .annotate(qty=Sum('quantity'))
        .order_by('-qty')
        .first()
    )
    
    # Unsold products
    unsold_products = Product.objects.filter(orderitem__isnull=True).order_by('name')[:10]
    
    # Total revenue
    total_revenue = (
        OrderItem.objects.aggregate(
            revenue=Sum(F('quantity') * F('price_per_unit'), output_field=DecimalField())
        )['revenue'] or 0
    )
    
    # Monthly revenue
    monthly_revenue = (
        OrderItem.objects.annotate(month=TruncMonth('order__sale_date'))
        .values('month')
        .annotate(
            revenue=Sum(F('quantity') * F('price_per_unit'), output_field=DecimalField())
        )
        .order_by('-month')[:12]
    )
    
    # Products by category
    products_by_category = ProductCategory.objects.annotate(
        product_count=Count('products')
    ).order_by('-product_count')
    
    # Average order value
    avg_order_value = Order.objects.aggregate(
        avg=Avg('order_items__quantity')
    )['avg'] or 0
    
    # Customers by city
    customers_by_city = Customer.objects.values('city').annotate(
        customer_count=Count('id')
    ).order_by('-customer_count')[:5]
    
    context = {
        'top_product': top_product,
        'unsold_products': unsold_products,
        'total_revenue': total_revenue,
        'monthly_revenue': list(monthly_revenue),
        'products_by_category': products_by_category,
        'avg_order_value': avg_order_value,
        'customers_by_city': list(customers_by_city),
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/statistics.html', context)


# Profile views
@login_required
def profile(request):
    """User profile"""
    customer = getattr(request.user, 'customer_profile', None)
    employee = getattr(request.user, 'employee_profile', None)
    
    orders = []
    if customer:
        orders = (
            Order.objects.filter(customer=customer)
            .select_related('promo_code', 'pickup_point')
            .prefetch_related('order_items__product')
            .order_by('-sale_date')
        )
    
    if request.method == 'POST':
        if customer:
            form = CustomerProfileForm(request.POST, instance=customer)
            if form.is_valid():
                form.save()
                messages.success(request, 'Профиль обновлён')
                return redirect('store:profile')
        else:
            # Create customer profile
            form = CustomerProfileForm(request.POST)
            if form.is_valid():
                customer = form.save(commit=False)
                customer.user = request.user
                customer.save()
                messages.success(request, 'Профиль создан')
                return redirect('store:profile')
    else:
        form = CustomerProfileForm(instance=customer)
    
    context = {
        'customer': customer,
        'employee': employee,
        'orders': orders,
        'form': form,
        'current_time_utc': timezone.now(),
        'current_time_local': timezone.localtime(),
    }
    return render(request, 'store/profile.html', context)


# Auth views
def login_view(request):
    """User login"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            logger.info(f'User logged in: {user.username}')
            messages.success(request, 'Вы вошли в аккаунт')
            return redirect('store:home')
        messages.error(request, 'Неверный логин или пароль')
    else:
        form = LoginForm(request)
    
    return render(request, 'store/login.html', {'form': form})


@require_POST
def logout_view(request):
    """User logout"""
    logout(request)
    logger.info('User logged out')
    messages.success(request, 'Вы вышли из аккаунта')
    return redirect('store:home')


def register(request):
    """User registration"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f'New user registered: {user.username}')
            messages.success(request, 'Регистрация успешна')
            return redirect('store:home')
        messages.error(request, 'Исправьте ошибки в форме')
    else:
        form = RegisterForm()
    
    return render(request, 'store/register.html', {'form': form})


# API endpoints
def api_currency_rates(request):
    """API endpoint for currency rates"""
    rates = get_currency_rates()
    return JsonResponse({'rates': rates})


def api_statistics(request):
    """API endpoint for statistics"""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    stats = {
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_revenue': float(
            OrderItem.objects.aggregate(
                total=Sum(F('quantity') * F('price_per_unit'), output_field=DecimalField())
            )['total'] or 0
        ),
    }
    return JsonResponse(stats)
