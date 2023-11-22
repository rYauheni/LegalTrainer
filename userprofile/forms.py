from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from captcha.fields import CaptchaField

import re

from userprofile.utils import USERNAME_VALIDATION, PASSWORD_VALIDATION


class RegisterUserForm(UserCreationForm):

    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-input'}),
        error_messages={'required': 'Это поле обязательно к заполнению'}
    )
    email = forms.EmailField(
        label='EMail',
        widget=forms.EmailInput(attrs={'class': 'form-input'}),
        error_messages={'required': 'Это поле обязательно к заполнению',
                        'invalid': 'Введите корректный адрес электронной почты (например, user@examplemail.com)'}
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        error_messages={'required': 'Это поле обязательно к заполнению'}
    )
    password2 = forms.CharField(
        label='Повтор пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        error_messages={'required': 'Это поле обязательно к заполнению'}
    )
    captcha = CaptchaField(
        label='Введите текст',
        error_messages={'required': 'Это поле обязательно к заполнению',
                        'invalid': 'Капча введена неверно'}
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < USERNAME_VALIDATION['min_length'] or len(username) > USERNAME_VALIDATION['max_length']:
            raise forms.ValidationError(
                f"Длина логина должна быть не менее {USERNAME_VALIDATION['min_length']} "
                f"и не более {USERNAME_VALIDATION['max_length']} символов."
            )

        if not re.match(USERNAME_VALIDATION['content'], username):
            raise forms.ValidationError(
                'Логин должен содержать только латинские буквы и цифры.'
            )

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')

        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < PASSWORD_VALIDATION['min_length'] or len(password1) > PASSWORD_VALIDATION['max_length']:
            raise forms.ValidationError(
                f"Длина пароля должна быть не менее {PASSWORD_VALIDATION['min_length']} "
                f"и не более {PASSWORD_VALIDATION['max_length']} символов."
            )

        if not re.match(PASSWORD_VALIDATION['requirements'], password1):
            raise forms.ValidationError(
                'Пароль должен содержать как минимум 1 заглавную, 1 строчную букву и 1 цифру'
            )

        if not re.match(PASSWORD_VALIDATION['content'], password1):
            raise forms.ValidationError(
                'Пароль должен содержать только латинские буквы и цифры.'
            )

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 != password2:
            raise forms.ValidationError('Пароли не совпадают.')

        return password2

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class UserProfileChangeForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if len(username) < USERNAME_VALIDATION['min_length'] or len(username) > USERNAME_VALIDATION['max_length']:
            raise forms.ValidationError(
                f"Длина логина должна быть не менее {USERNAME_VALIDATION['min_length']} "
                f"и не более {USERNAME_VALIDATION['max_length']} символов."
            )

        if not re.match(USERNAME_VALIDATION['content'], username):
            raise forms.ValidationError(
                'Логин должен содержать только латинские буквы и цифры.'
            )

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if (self.cleaned_data.get('username') or self.cleaned_data.get('email')) and not password:
            raise forms.ValidationError('Пароль обязателен для изменения логина или email.')
        return password


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label='Старый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Введите текущий пароль."
    )

    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Введите новый пароль."
    )

    new_password2 = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Повторно введите новый пароль для подтверждения."
    )
