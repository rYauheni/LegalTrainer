from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse_lazy, reverse
from django.core.exceptions import ValidationError

from .forms import UserProfileForm, UserPasswordChangeForm


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
