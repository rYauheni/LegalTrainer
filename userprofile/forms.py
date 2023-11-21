from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from captcha.fields import CaptchaField

import re


class RegisterUserForm(UserCreationForm):
    MIN_PASSWORD_LENGTH = 8
    MAX_PASSWORD_LENGTH = 20
    PASSWORD_COMPLEXITY = {
        'UPPER': 1,
        'LOWER': 1,
        'DIGIT': 1,
    }

    MIN_USERNAME_LENGTH = 4
    MAX_USERNAME_LENGTH = 20

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
        error_messages={'required': 'Это поле обязательно к заполнению',}
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

        if len(username) < self.MIN_USERNAME_LENGTH or len(username) > self.MAX_USERNAME_LENGTH:
            raise forms.ValidationError(
                f'Длина логина должна быть не менее {self.MIN_USERNAME_LENGTH} '
                f'и не более {self.MAX_USERNAME_LENGTH} символов.'
            )

        if not re.match("^[a-zA-Z0-9]+$", username):
            raise forms.ValidationError(
                'Логин должен содержать только латинские буквы и цифры.'
            )

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Пользователь с таким логином уже существует.')

        return username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')

        if len(password1) < self.MIN_PASSWORD_LENGTH or len(password1) > self.MAX_PASSWORD_LENGTH:
            raise forms.ValidationError(
                f'Длина пароля должна быть не менее {self.MIN_PASSWORD_LENGTH} '
                f'и не более {self.MAX_PASSWORD_LENGTH} символов.'
            )

        if not re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$', password1):
            raise forms.ValidationError(
                'Пароль должен содержать как минимум 1 заглавную, 1 строчную букву и 1 цифру'
            )

        if not re.match("^[a-zA-Z0-9]+$", password1):
            raise forms.ValidationError(
                'Пароль должен содержать только латинские буквы и цифры.'
            )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if (self.cleaned_data.get('username') or self.cleaned_data.get('email')) and not password:
            raise forms.ValidationError('Пароль обязателен для изменения логина или email.')
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if (username or email) and not password:
            raise forms.ValidationError('Пароль обязателен для изменения логина или email.')

        user = self.instance

        if password:
            if not user.check_password(password):
                raise forms.ValidationError('Неверный пароль.')


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
