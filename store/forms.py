from django.contrib.auth import password_validation
from store.models import Address
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

