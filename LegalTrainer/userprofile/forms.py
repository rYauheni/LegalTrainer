from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField


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
