from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy, reverse
from django.core.exceptions import ValidationError

from .forms import UserProfileForm, UserPasswordChangeForm

from quiz.models import Answer, Test, UserTestModel, UserTestAnswer


# Create your views here.

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


def get_change_pw_success(request):
    return render(request, 'userprofile/change_pw_success.html')


def show_history(request):
    user_tests = UserTestModel.objects.filter(user=request.user).order_by('-id')
    user_results = []
    for user_test in user_tests:
        user_test_questions = user_test.test.testquestion_set.order_by('order')
        user_answers = UserTestAnswer.objects.get(user_test=user_test)
        test_result = {}
        for user_test_question in user_test_questions:
            question = user_test_question.question

            test_result.setdefault(question, {
                'user_answers': [],
                'correct_answers': []
            })
            user_answers_list = user_answers.user_answers.filter(question=question)
            for u_answer in user_answers_list:
                test_result[question]['user_answers'].append(u_answer)

            if not test_result[question]['correct_answers']:
                correct_answers = Answer.objects.filter(question=question, correctness=True)
                for c_answer in correct_answers:
                    test_result[question]['correct_answers'].append(c_answer)
        user_results.append(test_result)
    len_results = len(user_results)
    user_results = [(len_results - i, user_results[i]) for i in range(len_results)]
    return render(request, 'userprofile/history.html', context={'user_results': user_results})

