from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView
from django.db.models import Max, Count

from random import shuffle, choice, choices

from .models import Category, Question, Answer, Test, UserTestModel, TestAnswer
from .forms import RegisterUserForm, LoginUserForm, AnswersForm


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


def set_test(request, slug_category):
    category_id = category_id = Category.objects.get(slug=slug_category)
    questions = Question.objects.filter(category=category_id)
    id_list = []
    for question in questions:
        id_list.append(question.id)
    shuffle(id_list)
    if len(id_list) >= 10:
        id_list = id_list[:10]
    questions = questions.filter(id__in=id_list).order_by('?')
    answers = Answer.objects.filter(question__in=id_list)
    #################################################################
    test = Test()
    test.save()
    for question in questions:
        test.questions.add(question)

    # test_answer = TestAnswer(test=test)
    # test_answer.save()
    # for answer in answers:
    #     test_answer.answers.add(answer)

    user_test = UserTestModel(user=request.user, test=test)
    user_test.save()
    #################################################################
    return render(request, 'quiz/CHECK_TEST.html', context={
        'questions': questions,
        'answers': answers
    })


def get_question(request):
    # questions = Test.objects.filter(user=request.user)
    # question, answers = None, None
    # if questions.aggregate(Count('is_answered')):
    #     for q in questions:
    #         if not q.is_answered:
    #             question = Question.objects.get(content=q.question)
    #             break
    #     answers = Answer.objects.filter(question=question.id)
    # else:
    #     pass  # ???????????? ???????????????????? ??????????
    # return render(request, 'quiz/question.html', context={
    #     'question': question,
    #     'answers': answers,
    #     'form': AnswersForm(),
    # })
    user_tests = UserTestModel.objects.filter(user=request.user)
    last_number = len(user_tests) - 1
    user_test = user_tests[last_number]
    counter = user_test.counter
    test = Test.objects.get(usertestmodel=user_test)
    questions = test.questions.all()
    question = questions[counter]
    answers = Answer.objects.filter(question=question)
    if 0 <= counter < 9:
        user_test.counter += 1
        user_test.save()
    elif counter == 9:
        pass  # ???????????? ???????????????????? ??????????
    else:
        raise ValueError('Counter value must be in range(0, 10)')
    return render(request, 'quiz/question.html', context={
        'user_test': user_test,
        'test': test,
        'questions': questions,
        'question': question,
        'answers': answers,
        'counter': counter,
    })
