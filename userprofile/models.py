from django.db import models
from django.conf import settings

from quiz.models import Category


class UserStat(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    correct = models.IntegerField(default=0)
    incorrect = models.IntegerField(default=0)
