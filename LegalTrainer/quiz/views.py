from django.contrib.auth import logout, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView
from django.db.models import Max, Count

from random import shuffle, choice, choices

from .models import Category, Question, Answer, Test, UserTestModel, UserTestAnswer
from .forms import RegisterUserForm, LoginUserForm, UserAnswersForm
from .utils import QUESTIONS_QUANTITY


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
    category_id = Category.objects.get(slug=slug_category)
    questions = Question.objects.filter(category=category_id)
    id_list = [question.id for question in questions]
    shuffle(id_list)
    if len(id_list) >= QUESTIONS_QUANTITY:
        id_list = id_list[:QUESTIONS_QUANTITY]
    questions = questions.filter(id__in=id_list).order_by('?')
    answers = Answer.objects.filter(question__in=id_list)
    #################################################################
    test = Test()
    test.save()
    for question in questions:
        test.questions.add(question)  # Результат упорядоченный

    # test_answer = TestAnswer(test=test)
    # test_answer.save()
    # for answer in answers:
    #     test_answer.answers.add(answer)

    user_test = UserTestModel(user=request.user, test=test, counter=0)
    user_test.save()
    #################################################################
    #################
    UserTestAnswer(user_test=user_test).save()

    return render(request, 'quiz/CHECK_TEST.html', context={
        'questions': questions,
        'answers': answers
    })


def get_question(request, q_number):
    # questions = Test.objects.filter(user=request.user)
    # question, answers = None, None
    # if questions.aggregate(Count('is_answered')):
    #     for q in questions:
    #         if not q.is_answered:
    #             question = Question.objects.get(content=q.question)
    #             break
    #     answers = Answer.objects.filter(question=question.id)
    # else:
    #     pass  # ЛОГИКА ЗАВЕРШЕНИЯ ТЕСТА
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
    answers = Answer.objects.filter(question=question).order_by('?')


    #################
    form = UserAnswersForm(answers=answers)
    #################

    if request.method == 'GET':
        return render(request, 'quiz/question.html', context={
            'user_test': user_test,
            'test': test,
            'questions': questions,
            'question': question,
            'answers': answers,
            'counter': counter,
            'quantity': QUESTIONS_QUANTITY,
            'form': form,
        })
    elif request.method == 'POST':
        form = UserAnswersForm(request.POST, answers=answers)

        form.full_clean()
        id_user_answers = form.cleaned_data
        print(id_user_answers)
        #################
        user_test_answers = UserTestAnswer.objects.get(user_test=user_test)
        for id_a in id_user_answers['answers']:
            user_test_answers.user_answers.add(Answer.objects.get(id=id_a))



        #################

        if 0 <= counter <= QUESTIONS_QUANTITY - 1:
            url = reverse('question_url', args=(q_number,))
            if form.is_valid():
                if 'previous' in request.POST:  # КНОПКА PREVIOUS срабатывает корректно на последнем вопросе теста, т.к. попадает в блок ELIF
                    user_test.counter -= 1
                    user_test.save()
                    q_number = user_test.counter
                    url = reverse('question_url', args=(q_number,))
                elif 'next' in request.POST:
                    user_test.counter += 1
                    user_test.save()
                    q_number = user_test.counter
                    url = reverse('question_url', args=(q_number,))
                elif 'end' in request.POST:
                    url = reverse('result_url')

        else:
            raise ValueError(f'Counter value must be in range(0, {QUESTIONS_QUANTITY})')
        return redirect(url)


def show_test_result(request):
    user_tests = UserTestModel.objects.filter(user=request.user)
    last_number = len(user_tests) - 1
    user_test = user_tests[last_number]
    user_answers = UserTestAnswer.objects.get(user_test=user_test)
    full_result = {}
    for u_answer in user_answers.user_answers.all():
        question = u_answer.question
        full_result.setdefault(question, {
            'user_answers': [],
            'correct_answers': []
        })
        full_result[question]['user_answers'].append(u_answer)

        if not full_result[question]['correct_answers']:
            correct_answers = Answer.objects.filter(question=question)
            for c_answer in correct_answers:
                if c_answer.correctness:
                    full_result[question]['correct_answers'].append(c_answer)
    quantity_questions = len(full_result)
    success_questions = 0
    for key in full_result:
        if full_result[key]['user_answers'] == full_result[key]['correct_answers']:
            success_questions += 1
    correctness_percent = round((100 / quantity_questions * success_questions), 2)

    return render(request, 'quiz/test_result.html', context={
        'full_result': full_result,
        'quantity_questions': quantity_questions,
        'success_questions': success_questions,
        'correctness_percent': correctness_percent,
    })
