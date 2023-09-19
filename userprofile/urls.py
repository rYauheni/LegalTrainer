from django.urls import path

from . import views

urlpatterns = [
    path('profile', views.show_profile, name='profile_url'),

    path('profile/change-pdata', views.change_profile_data, name='change_pd_url'),
    path('profile/change-pdata/success', views.get_change_pd_success, name='change_pd_success_url'),
    path('profile/change-password', views.change_password, name='change_pw_url'),
    path('profile/change-password/success', views.get_change_pw_success, name='change_pw_success_url'),

    path('profile/history', views.show_history, name='history_url'),

    path('profile/stat', views.show_stat, name='stat_url'),

]
