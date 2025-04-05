from django.contrib.auth import password_validation
from store.models import Address, Product, Category
from django import forms
import django
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UsernameField, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.db import models
from django.db.models import fields
from django.forms import widgets
from django.forms.fields import CharField
from django.utils.translation import gettext, gettext_lazy as _
from .models import Review, RATING_CHOICES



class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Пароль'}))
    password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput(attrs={'class':'form-control', 'placeholder':'Подтвердите пароль'}))
    email = forms.CharField(required=True, widget=forms.EmailInput(attrs={'class':'form-control', 'placeholder':'Email адрес'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {'email': 'Email', 'username': 'Имя пользователя'}
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Имя пользователя'})}


class LoginForm(AuthenticationForm):
    username = UsernameField(widget=forms.TextInput(attrs={
        'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
        'placeholder': 'Имя пользователя'
    }))
    password = forms.CharField(
        label=_("Пароль"),
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Пароль',
            'autocomplete': 'current-password'
        })
    )


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['locality', 'city', 'state']
        widgets = {
            'locality': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Популярное место, например ресторан, религиозное место и т.д.'}),
            'city': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Город'}),
            'state': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Область или регион'})
        }


class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label=_("Текущий пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password', 'auto-focus':True, 'class':'form-control', 'placeholder':'Текущий пароль'}))
    new_password1 = forms.CharField(label=_("Новый пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control', 'placeholder':'Новый пароль'}), help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("Подтвердите новый пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control', 'placeholder':'Подтвердите новый пароль'}))


class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label=_("Email"), max_length=254, widget=forms.EmailInput(attrs={'autocomplete':'email', 'class':'form-control', 'placeholder': 'Email адрес'}))


class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(label=_("Новый пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control', 'placeholder': 'Новый пароль'}), help_text=password_validation.password_validators_help_text_html())
    new_password2 = forms.CharField(label=_("Подтвердите новый пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password', 'class':'form-control', 'placeholder': 'Подтвердите новый пароль'}))


class ReviewForm(forms.ModelForm):
    """Форма для добавления отзывов к товарам"""
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-input'}),
        label="Оценка"
    )
    
    comment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Напишите ваш отзыв о товаре',
            'rows': 4
        }),
        label="Ваш отзыв"
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class CategoryForm(forms.ModelForm):
    """Форма для добавления/редактирования категорий"""
    
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Название категории'
        }),
        label="Название"
    )
    
    slug = forms.SlugField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'URL категории (например: jewelry)'
        }),
        label="Slug"
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Описание категории',
            'rows': 3
        }),
        label="Описание",
        required=False
    )
    
    category_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
        }),
        label="Изображение категории",
        required=False
    )
    
    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-secondary focus:ring-secondary border-gray-300 rounded'
        }),
        label="Активная категория",
        required=False,
        initial=True
    )
    
    is_featured = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-secondary focus:ring-secondary border-gray-300 rounded'
        }),
        label="Рекомендуемая категория",
        required=False
    )
    
    class Meta:
        model = Category
        fields = ['title', 'slug', 'description', 'category_image', 'is_active', 'is_featured']


class ProductForm(forms.ModelForm):
    """Форма для добавления/редактирования товаров"""
    
    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Название товара'
        }),
        label="Название"
    )
    
    slug = forms.SlugField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'URL товара (например: gold-ring)'
        }),
        label="Slug"
    )
    
    sku = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Уникальный ID товара (например: JW-001)'
        }),
        label="Артикул (SKU)",
        required=False
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
        }),
        label="Категория"
    )
    
    short_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Краткое описание товара',
            'rows': 3
        }),
        label="Краткое описание"
    )
    
    detail_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Подробное описание товара',
            'rows': 5
        }),
        label="Подробное описание",
        required=False
    )
    
    price = forms.DecimalField(
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Цена товара',
            'min': 0,
            'step': 0.01
        }),
        label="Цена (₸)"
    )
    
    product_image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent',
        }),
        label="Изображение товара",
        required=False
    )
    
    is_active = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-secondary focus:ring-secondary border-gray-300 rounded'
        }),
        label="Активный товар",
        required=False,
        initial=True
    )
    
    is_featured = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'h-4 w-4 text-secondary focus:ring-secondary border-gray-300 rounded'
        }),
        label="Рекомендуемый товар",
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['title', 'slug', 'sku', 'category', 'short_description', 'detail_description', 'price', 'product_image', 'is_active', 'is_featured']

