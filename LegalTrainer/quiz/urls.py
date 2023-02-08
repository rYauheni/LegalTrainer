from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index),
    path('quiz/question/<question_id>', views.get_question)
]