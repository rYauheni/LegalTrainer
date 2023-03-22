from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField

from .models import Answer


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='EMail', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    captcha = CaptchaField(label='Введите текст')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))


class UserAnswersForm(forms.Form):
    # answers = forms.MultipleChoiceField(required=False, widget=forms.CheckboxSelectMultiple, )

    def __init__(self, *args, answers, **kwargs):
        super().__init__(*args, **kwargs)
        answers = answers
        for i in range(len(answers)):
            field_name = f'{chr(97 + i)}. {answers[i].content}'
            self.fields[field_name] = forms.MultipleChoiceField(
                required=False,
                widget=forms.CheckboxSelectMultiple,
            )
            try:
                self.initial[field_name] = answers[i].content
            except IndexError:
                self.initial[field_name] = 'error'

    def get_answers_fields(self):
        for field_name in self.fields:
            yield self[field_name]
