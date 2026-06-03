from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Review, Customer, Order, OrderItem
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        required=True,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class CustomerProfileForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^\+375 \(2[59]\) \d{3}-\d{2}-\d{2}$',
        message='Формат: +375 (29) XXX-XX-XX'
    )
    phone = forms.CharField(
        validators=[phone_regex],
        max_length=20,
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'placeholder': '+375 (29) XXX-XX-XX',
            'class': 'form-input',
            'style': 'width: 100%; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 14px;'
        })
    )

    class Meta:
        model = Customer
        fields = ['phone', 'address', 'city', 'birth_date', 'preferred_pickup']
        widgets = {
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input',
                'style': 'width: 100%; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 14px;'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-input',
                'style': 'width: 100%; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 14px;'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-input',
                'style': 'width: 100%; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 14px;',
                'placeholder': 'Минск'
            }),
            'preferred_pickup': forms.Select(attrs={
                'class': 'form-input',
                'style': 'width: 100%; padding: 12px 15px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: 14px;'
            }),
        }

    def clean_birth_date(self):
        from datetime import date
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )
            if age < 18:
                raise forms.ValidationError('Возраст должен быть не менее 18 лет.')
        return birth_date


class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [(i, '⭐' * i) for i in range(1, 6)]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        label='Оценка',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = Review
        fields = ['name', 'rating', 'text']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ваше имя'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв...'
            }),
        }


class ProductFilterForm(forms.Form):
    search = forms.CharField(
        required=False,
        label='Поиск',
        widget=forms.TextInput(attrs={
            'placeholder': 'Название товара...',
            'class': 'form-input',
            'name': 'q'
        })
    )
    category = forms.ChoiceField(
        required=False,
        label='Категория',
        choices=[],  # Will be populated in view
        widget=forms.Select(attrs={'class': 'form-input', 'name': 'category'})
    )
    price_min = forms.DecimalField(
        required=False,
        label='Цена от',
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '0',
            'name': 'min_price'
        })
    )
    price_max = forms.DecimalField(
        required=False,
        label='Цена до',
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': '9999',
            'name': 'max_price'
        })
    )
    sort = forms.ChoiceField(
        required=False,
        label='Сортировка',
        choices=[
            ('name', 'По названию А-Я'),
            ('-name', 'По названию Я-А'),
            ('price', 'Сначала дешевле'),
            ('-price', 'Сначала дороже'),
        ],
        widget=forms.Select(attrs={'class': 'form-input', 'name': 'sort'})
    )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pickup_point', 'promo_code']
        widgets = {
            'pickup_point': forms.Select(attrs={'class': 'form-input'}),
            'promo_code': forms.Select(attrs={'class': 'form-input'}),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)