from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView

from .models import Category, Question, Answer
from .forms import RegisterUserForm, LoginUserForm


# Create your views here.

def index(request):
    return render(request, 'quiz/index.html')


# def choose_category(request):
#     categories = Category.objects.order_by('title')
#     return render(request, 'quiz/categories.html', context={'categories': categories})


class CategoryListView(ListView):
    model = Category
    template_name = 'quiz/categories.html'
    context_object_name = 'categories'


# def show_category(request, slug_category):
#     category = get_object_or_404(Category, slug=slug_category)
#     return render(request, 'quiz/category.html', context={'category': category})


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'quiz/category.html'
    slug_url_kwarg = 'slug_category'
    context_object_name = 'category'


def get_question(request, question_id):
    question = Question.objects.get(id=question_id)
    answers = Answer.objects.filter(question=question.id)
    return render(request, 'quiz/question.html', context={
        'question': question,
        'answers': answers
    })


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'quiz/register.html'
    success_url = reverse_lazy('reg_success_url')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('reg_success_url')


def get_register_success(request):
    return render(request, 'quiz/reg_success.html')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'quiz/login.html'

    def get_success_url(self):
        return reverse_lazy('index_url')


def logout_user(request):
    logout(request)
    return redirect('login_url')
