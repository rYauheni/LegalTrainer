from django.urls import reverse

QUESTIONS_QUANTITY = 10


class BarMixin:
    def post(self, request, *args, **kwargs):
        if 'login' in request.POST:
            return reverse('login_url')
        elif 'logout' in request.POST:
            return reverse('logout_url')
        elif 'register' in request.POST:
            return reverse('register_url')
        elif 'profile' in request.POST:
            return reverse('profile_url')
