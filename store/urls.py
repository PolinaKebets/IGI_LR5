# store/urls.py
# ПОЛНОСТЬЮ ЗАМЕНИТЬ ФАЙЛ НА ЭТОТ:

from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'store'

urlpatterns = [
    path("", views.home, name="home"),

    # Reviews — ТОЛЬКО ЭТИ 4 МАРШРУТА
    path('reviews/', views.reviews, name='reviews'),
    path('reviews/add/', views.add_review, name='add_review'),
    path('reviews/<int:review_id>/edit/', views.edit_review, name='edit_review'),
    path('reviews/<int:review_id>/delete/', views.delete_review, name='delete_review'),

    # auth
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),

    # pages
    path("about/", views.about, name="about"),
    path("calendar/", views.calendar_view, name="calendar"),

    path("news/", views.news_list, name="news"),
    re_path(r"^news/(?P<pk>\d+)/$", views.news_detail, name="news_detail"),

    path("glossary/", views.glossary_list, name="glossary"),
    path("contacts/", views.contacts, name="contacts"),
    path("vacancies/", views.vacancies, name="vacancies"),
    path("privacy/", views.privacy, name="privacy"),

    path("promocodes/", views.promocodes, name="promo_codes"),

    # products
    path("products/", views.product_list, name="product_list"),
    re_path(r"^products/(?P<pk>\d+)/$", views.product_detail, name="product_detail"),

    # orders (CRUD)
    path("orders/", views.order_list, name="order_list"),
    re_path(r"^orders/(?P<pk>\d+)/$", views.order_detail, name="order_detail"),
    path("orders/create/", views.order_create, name="order_create"),
    re_path(r"^orders/(?P<pk>\d+)/update/$", views.order_update, name="order_update"),
    re_path(r"^orders/(?P<pk>\d+)/delete/$", views.order_delete, name="order_delete"),
    re_path(r"^orders/(?P<pk>\d+)/cancel/$", views.order_cancel, name="order_cancel"),

    # employee
    path("employee/", views.employee_dashboard, name="employee_dashboard"),

    # cabinet/statistics
    path("profile/", views.profile, name="profile"),
    path("statistics/", views.statistics, name="statistics"),

    # API
    path("api/currency-rates/", views.api_currency_rates, name="api_currency_rates"),
    path("api/statistics/", views.api_statistics, name="api_statistics"),
    path("api/reviews/", views.api_format_reviews, name="api_format_reviews"),
    path("api/reviews/<int:review_id>/delete/", views.api_delete_review, name="api_delete_review"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)