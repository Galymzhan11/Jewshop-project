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
    username = UsernameField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control', 'placeholder': 'Имя пользователя'}))
    password = forms.CharField(label=_("Пароль"), strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password', 'class':'form-control', 'placeholder': 'Пароль'}))


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

