from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField

from .models import Answer


# class UserAnswersForm(forms.Form):
#
#     def __init__(self, *args, answers, **kwargs):
#         super().__init__(*args, **kwargs)
#         answers = answers
#         self.fields['answers'] = forms.MultipleChoiceField(
#             required=False,
#             widget=forms.CheckboxSelectMultiple,
#             choices=((f'{i}', f'{chr(97 + i)}. {answers[i].content}') for i in range(len(answers)))
#         )
#         for i in range(len(answers)):
#             field_name = f'{chr(97 + i)}. {answers[i].content}'
#             try:
#                 self.initial[field_name] = answers[i].content
#             except IndexError:
#                 self.initial[field_name] = 'error'
#
#     def get_answers_fields(self):
#         answers_id = []
#         for field in self.fields['answers']:
#             answers_id.append(field)
#         return answers_id


class UserAnswersForm(forms.Form):

    def __init__(self, *args, answers, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['answers'] = forms.MultipleChoiceField(
            required=False,
            widget=forms.CheckboxSelectMultiple,
            choices=((f'{answers[i].id}', f'{chr(97 + i)}. {answers[i].content}') for i in range(len(answers))))

    def clean_answers(self):
        return [int(answer_id) for answer_id in self.cleaned_data['answers']]
