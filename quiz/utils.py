from django.urls import reverse

QUESTIONS_QUANTITY = 10


class BarMixin:
    def post(self, request, *args, **kwargsфв):
        if 'login' in request.POST:
            return reverse('login_url')
        elif 'profile' in request.POST:
            return reverse('profile_url')
