from django.db import models
from django.conf import settings
# from django.utils.text import slugify
from django.urls import reverse
from pytils.translit import slugify


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=60)
    slug = models.SlugField(max_length=16, unique=True, db_index=True, null=False)

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_url', kwargs={'slug_category': self.slug})

    class Meta:
        ordering = ['title']


class Question(models.Model):
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    content = models.TextField()

    def __str__(self):
        return f'{self.content}'


class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    content = models.TextField()
    correctness = models.BooleanField()

    def __str__(self):
        return f'{self.content}'


class Test(models.Model):
    date = models.DateField(auto_now_add=True)
    questions = models.ManyToManyField('Question', blank=True)


class TestQuestion(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()


class UserTestModel(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    counter = models.IntegerField(default=0)


class UserTestAnswer(models.Model):  ##### модель для ответа пользователя на тест
    user_test = models.OneToOneField('UserTestModel', on_delete=models.SET_NULL, null=True, blank=True)
    user_answers = models.ManyToManyField('Answer', blank=True)


class UserTestResult(models.Model):
    user_test = models.ForeignKey('UserTestModel', on_delete=models.CASCADE)
    user_test_category = models.ForeignKey('Category', on_delete=models.CASCADE)
    correct = models.IntegerField(default=0)
    incorrect = models.IntegerField(default=0)
