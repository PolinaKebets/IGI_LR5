from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Company, CompanyHistory, Article, Glossary, Contact,
    Vacancy, Review, PromoCode, Manufacturer, ProductCategory,
    Product, PickupPoint, Customer, Employee, Order, OrderItem
)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone']
    search_fields = ['name', 'email']


@admin.register(CompanyHistory)
class CompanyHistoryAdmin(admin.ModelAdmin):
    list_display = ['year', 'company', 'event']
    list_filter = ['company']
    ordering = ['year']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_date', 'is_published']
    list_filter = ['is_published', 'published_date']
    search_fields = ['title', 'summary', 'content']
    list_editable = ['is_published']
    date_hierarchy = 'published_date'


@admin.register(Glossary)
class GlossaryAdmin(admin.ModelAdmin):
    list_display = ['question', 'added_date']
    search_fields = ['question', 'answer']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'position', 'phone', 'email']
    search_fields = ['first_name', 'last_name', 'position']


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ['title', 'salary_min', 'salary_max', 'is_active', 'created_date']
    list_filter = ['is_active']
    list_editable = ['is_active']
    search_fields = ['title', 'description']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'date', 'user']
    list_filter = ['rating']
    search_fields = ['name', 'text']
    date_hierarchy = 'date'


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_percent', 'valid_from',
                    'valid_to', 'is_active', 'is_valid_display']
    list_filter = ['is_active']
    list_editable = ['is_active']
    search_fields = ['code', 'description']

    def is_valid_display(self, obj):
        if obj.is_valid:
            return format_html('<span style="color:green;">✓ Действует</span>')
        return format_html('<span style="color:red;">✗ Недействителен</span>')
    is_valid_display.short_description = 'Статус'


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'website']
    search_fields = ['name', 'country']
    list_filter = ['country']


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'unit',
                    'stock_quantity', 'is_available']
    list_filter = ['category', 'is_available', 'unit']
    list_editable = ['price', 'is_available', 'stock_quantity']
    search_fields = ['name', 'description']
    filter_horizontal = ['manufacturers']
    date_hierarchy = 'created_date'


@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ['address', 'city', 'phone', 'working_hours']
    list_filter = ['city']
    search_fields = ['address', 'city']


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'city', 'birth_date', 'age_display']
    search_fields = ['user__username', 'user__first_name',
                     'user__last_name', 'phone']
    list_filter = ['city']

    def age_display(self, obj):
        age = obj.age
        if age is not None:
            if age < 18:
                return format_html(
                    '<span style="color:red;">{} (нет 18)</span>', age)
            return age
        return '-'
    age_display.short_description = 'Возраст'


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'birth_date', 'hire_date']
    list_filter = ['role']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal_display']

    def subtotal_display(self, obj):
        if obj.pk:
            return f"{obj.subtotal} BYN"
        return '-'
    subtotal_display.short_description = 'Итого'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'employee', 'status',
                    'sale_date', 'total_price_display']
    list_filter = ['status', 'sale_date']
    search_fields = ['customer__user__username',
                     'customer__user__first_name']
    list_editable = ['status']
    date_hierarchy = 'sale_date'
    inlines = [OrderItemInline]

    def total_price_display(self, obj):
        return f"{obj.total_price} BYN"
    total_price_display.short_description = 'Сумма'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity',
                    'price_per_unit', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['product__name']