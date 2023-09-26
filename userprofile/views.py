from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.core.exceptions import ValidationError
from django.views.generic import CreateView, ListView, DetailView

from .models import UserStat
from .forms import RegisterUserForm, LoginUserForm, UserProfileForm, UserPasswordChangeForm
from .utils import show_pie_histogram, show_bar_histogram
from .tasks import cleanup_old_images

from quiz.models import Category, Answer, Test, UserTestModel, UserTestAnswer, UserTestResult


import time

# Create your views here.


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'userprofile/register.html'
    success_url = reverse_lazy('reg_success_url')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('reg_success_url')


def get_register_success(request):
    return render(request, 'userprofile/reg_success.html')


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'userprofile/login.html'

    def get_success_url(self):
        return reverse_lazy('index_url')


def logout_user(request):
    logout(request)
    return redirect('login_url')


def show_profile(request):
    if request.method == 'GET':
        return render(request, 'userprofile/profile.html')
    elif request.method == 'POST':
        url = reverse('profile_url')
        if 'change_pd' in request.POST:
            url = reverse('change_pd_url')
        elif 'change_pw' in request.POST:
            url = reverse('change_pw_url')
        return redirect(url)


def change_profile_data(request):
    user = request.user
    user_data = {'username': user.username, 'email': user.email}
    if request.method == 'GET':
        form = UserProfileForm(instance=user)
        return render(request, 'userprofile/change_profile_data.html', context={
            'form': form,
            'user_data': user_data,
        })
    elif request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            if form.cleaned_data['password']:
                if not user.check_password(form.cleaned_data['password']):
                    form.add_error('password', 'Неверный пароль.')
                    return render(request, 'userprofile/change_profile_data.html', context={
                        'form': form,
                        'user_data': user_data,
                    })
                else:
                    form.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Профиль успешно обновлен.')
                    return redirect('change_pd_success_url')
        else:
            return render(request, 'userprofile/change_profile_data.html', context={
                'form': form,
                'user_data': user_data,
            })


def get_change_pd_success(request):
    return render(request, 'userprofile/change_pd_success.html')


def change_password(request):
    if request.method == 'GET':
        form = UserPasswordChangeForm(request.user)
        return render(request, 'userprofile/change_password.html', context={
            'form': form,
        })
    elif request.method == 'POST':
        form = UserPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)  # Обновление хеша сессии
            messages.success(request, 'Пароль успешно изменен.')
            return redirect('change_pw_success_url')
        else:
            return render(request, 'userprofile/change_password.html', context={
                'form': form,
            })


def get_change_pw_success(request):
    return render(request, 'userprofile/change_pw_success.html')


# def show_history(request):
#     user_tests = UserTestModel.objects.filter(user=request.user).order_by('-id')
#     user_results = []
#     for user_test in user_tests:
#         user_test_questions = user_test.test.testquestion_set.order_by('order')
#         user_answers = UserTestAnswer.objects.get(user_test=user_test)
#         test_result = {}
#         for user_test_question in user_test_questions:
#             question = user_test_question.question
#
#             test_result.setdefault(question, {
#                 'user_answers': [],
#                 'correct_answers': []
#             })
#             user_answers_list = user_answers.user_answers.filter(question=question)
#             for u_answer in user_answers_list:
#                 test_result[question]['user_answers'].append(u_answer)
#
#             if not test_result[question]['correct_answers']:
#                 correct_answers = Answer.objects.filter(question=question, correctness=True)
#                 for c_answer in correct_answers:
#                     test_result[question]['correct_answers'].append(c_answer)
#         user_results.append(test_result)
#     len_results = len(user_results)
#     user_results = [(len_results - i, user_results[i]) for i in range(len_results)]
#     return render(request, 'userprofile/history.html', context={'user_results': user_results})


class UserTestHistoryListView(ListView):
    template_name = 'userprofile/history.html'
    model = UserTestModel
    context_object_name = 'user_tests'
    paginate_by = 10

    def get_queryset(self):
        return UserTestModel.objects.filter(user=self.request.user).order_by('-id')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_tests = context['user_tests']
        user_test_results = {user_test: {'is_finished': False, 'category': '', 'correct': 0, 'incorrect': 0, 'number': 0} for user_test in user_tests}

        page_number = self.request.GET.get('page')
        page_number = int(page_number) if page_number else 1
        counter = len(self.get_queryset()) - ((page_number - 1) * self.paginate_by)

        for user_test in user_tests:
            try:
                user_test_result = UserTestResult.objects.get(user_test=user_test)
            except UserTestResult.DoesNotExist:
                user_test_result = 0
            if user_test_result:
                category = user_test_result.user_test_category
                correct = user_test_result.correct
                incorrect = user_test_result.incorrect
                user_test_results[user_test]['is_finished'] = True
                user_test_results[user_test]['category'] = category
                user_test_results[user_test]['correct'] = correct
                user_test_results[user_test]['incorrect'] = incorrect
            user_test_results[user_test]['number'] = counter
            counter -= 1

        context['user_tests'] = user_test_results

        #     categories_stat = {category.title: {'questions': 0, 'correct': 0, 'incorrect': 0, 'his_pie': ''} for category in
        #                        categories}


        # # Получить список объектов UserTestModel из контекста
        # user_tests = context['user_tests']
        #
        # # Создадим список для хранения категорий
        # category_titles = []
        #
        # for user_test in user_tests:
        #     test = user_test.test  # Получить связанный объект Test
        #     first_test_question = test.testquestion_set.first()  # Получить первый объект TestQuestion
        #
        #     if first_test_question:
        #         category_title = first_test_question.question.category.title
        #     else:
        #         category_title = None  # Обработка случая, если нет вопросов в тесте
        #
        #     category_titles.append(category_title)
        #
        # context['user_test_cats'] = category_titles
        return context

    # def get_queryset(self):
    #     user_tests = UserTestModel.objects.filter(user=self.request.user).order_by('-id')
    #     user_results = []
    #
    #     for user_test in user_tests:
    #         user_test_questions = user_test.test.testquestion_set.order_by('order')
    #         user_answers = UserTestAnswer.objects.get(user_test=user_test)
    #         test_result = {}
    #
    #         for user_test_question in user_test_questions:
    #             question = user_test_question.question
    #             test_result.setdefault(question, {
    #                 'user_answers': [],
    #                 'correct_answers': []
    #             })
    #             user_answers_list = user_answers.user_answers.filter(question=question)
    #             for u_answer in user_answers_list:
    #                 test_result[question]['user_answers'].append(u_answer)
    #
    #             if not test_result[question]['correct_answers']:
    #                 correct_answers = Answer.objects.filter(question=question, correctness=True)
    #                 for c_answer in correct_answers:
    #                     test_result[question]['correct_answers'].append(c_answer)
    #
    #         user_results.append(test_result)
    #
    #     len_results = len(user_results)
    #     user_results = [(len_results - i, user_results[i]) for i in range(len_results)]
    #
    #     return user_results


class UserTestDetailView(DetailView):
    template_name = 'userprofile/history_detail.html'
    model = UserTestModel
    context_object_name = 'user_test'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_test = self.get_object()
        test = user_test.test
        user_test_questions = test.testquestion_set.order_by('order')
        user_answers = UserTestAnswer.objects.get(user_test=user_test)
        user_test_result = UserTestResult.objects.get(user_test=user_test)
        full_user_test_result = {}
        for user_test_question in user_test_questions:
            question = user_test_question.question
            answers = Answer.objects.filter(question=question)

            full_user_test_result.setdefault(
                question, {
                    'answers': answers,
                    'user_answers': [],
                    'correct_answers': []
                }
            )

            user_answers_list = user_answers.user_answers.filter(question=question)
            for u_answer in user_answers_list:
                full_user_test_result[question]['user_answers'].append(u_answer)

            if not full_user_test_result[question]['correct_answers']:
                correct_answers = Answer.objects.filter(question=question, correctness=True)
                for c_answer in correct_answers:
                    full_user_test_result[question]['correct_answers'].append(c_answer)

        context['user_test_result'] = user_test_result
        context['full_user_test_result'] = full_user_test_result
        return context


# def show_stat(request):
#     p1 = time.time()
#     cleanup_old_images()
#     user_tests = UserTestModel.objects.filter(user=request.user)
#     total_tests = user_tests.count()
#     total_questions = 0
#     correct_questions = 0
#     incorrect_questions = 0
#     categories = Category.objects.all()
#     categories_stat = {category.title: {'questions': 0, 'correct': 0, 'incorrect': 0, 'his_pie': ''} for category in
#                        categories}
#     p2 = time.time()
#     for user_test in user_tests:
#         user_test_questions = user_test.test.testquestion_set.order_by('order')
#         total_questions += user_test_questions.count()
#         total_user_answers = UserTestAnswer.objects.get(user_test=user_test)
#         for user_test_question in user_test_questions:
#             question = user_test_question.question
#             question_category = question.category.title
#             categories_stat[question_category]['questions'] += 1
#             correct_answers = [c_a for c_a in Answer.objects.filter(question=question, correctness=True)]
#             user_answers_list = total_user_answers.user_answers.filter(question=question)
#             user_answers = []
#             for u_answer in user_answers_list:
#                 user_answers.append(u_answer)
#             if user_answers == correct_answers:
#                 correct_questions += 1
#                 categories_stat[question_category]['correct'] += 1
#             else:
#                 incorrect_questions += 1
#                 categories_stat[question_category]['incorrect'] += 1
#     p3 = time.time()
#     for cat in categories_stat:
#         categories_stat[cat]['his_pie'] = show_pie_histogram(categories_stat[cat]['correct'],
#                                                              categories_stat[cat]['incorrect'])
#     p4 = time.time()
#     total_his_pie = show_pie_histogram(correct_questions, incorrect_questions)
#     total_his_bar = show_bar_histogram(labels=tuple(cat for cat in categories_stat),
#                                        vals=tuple(v['questions'] for v in categories_stat.values()))
#     p5 = time.time()
#     with open('check_speed.py', 'a+') as f:
#         f.write(f'{request.user} - {p1, p2, p3, p4, p5}\n')
#     return render(request, 'userprofile/stat.html', context={
#         'total_tests': total_tests,
#         'total_questions': total_questions,
#         'correct_questions': correct_questions,
#         'incorrect_questions': incorrect_questions,
#         'total_his_pie': total_his_pie,
#         'total_his_bar': total_his_bar,
#         'categories_stat': categories_stat,
#
#     })


def show_stat(request):
    cleanup_old_images()
    user_tests = UserTestModel.objects.filter(user=request.user)
    total_tests = user_tests.count()
    total_questions = 0
    correct_questions = 0
    incorrect_questions = 0
    categories = Category.objects.all()
    categories_stat = {category.title: {'questions': 0, 'correct': 0, 'incorrect': 0, 'his_pie': ''} for category in
                       categories}

    #####  NEW

    user_stats = UserStat.objects.filter(user=request.user)
    for stat in user_stats:
        category = stat.category.title
        correct = stat.correct
        incorrect = stat.incorrect
        questions = correct + incorrect
        total_questions += questions
        correct_questions += correct
        incorrect_questions += incorrect
        categories_stat[category]['questions'] += questions
        categories_stat[category]['correct'] += correct
        categories_stat[category]['incorrect'] += incorrect
        categories_stat[category]['his_pie'] += show_pie_histogram(categories_stat[category]['correct'],
                                                                   categories_stat[category]['incorrect'])

    ####

    total_his_pie = show_pie_histogram(correct_questions, incorrect_questions)
    total_his_bar = show_bar_histogram(labels=tuple(cat for cat in categories_stat),
                                       vals=tuple(v['questions'] for v in categories_stat.values()))
    return render(request, 'userprofile/stat.html', context={
            'total_tests': total_tests,
            'total_questions': total_questions,
            'correct_questions': correct_questions,
            'incorrect_questions': incorrect_questions,
            'total_his_pie': total_his_pie,
            'total_his_bar': total_his_bar,
            'categories_stat': categories_stat,

    })
