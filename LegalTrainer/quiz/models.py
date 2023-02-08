from django.db import models


# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=60)

    def __str__(self):
        return f'{self.title}'


class Question(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, null=True)
    content = models.TextField()

    def __str__(self):
        return f'{self.content}'


class Answer(models.Model):
    question = models.ForeignKey('Question', on_delete=models.CASCADE, null=True)
    content = models.TextField()
    correctness = models.BooleanField()

    def __str__(self):
        return f'{self.content}'
