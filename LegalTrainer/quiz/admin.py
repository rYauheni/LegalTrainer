from django.contrib import admin
from .models import Category, Question, Answer


# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug']
    list_editable = ['title']
    search_fields = ['title']
    readonly_fields = ['slug']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'content', 'category']
    list_editable = ['content']
    search_fields = ['content']
    list_filter = ['category']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'content', 'correctness']
    list_editable = ['content', 'correctness']
    search_fields = ['content']
    list_filter = ['question']
