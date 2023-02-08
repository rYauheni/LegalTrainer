from django.shortcuts import render
from django.http import HttpResponseNotFound

from .models import Category, Question, Answer


# Create your views here.

def index(request):
    return render(request, 'quiz/index.html')


def get_question(request, question_id):
    question = Question.objects.get(id=question_id)
    answers = Answer.objects.filter(question=question.id)
    return render(request, 'quiz/question.html', context={
        'question': question,
        'answers': answers
    })

