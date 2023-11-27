from django.urls import path

from . import views

urlpatterns = [
    path('register', views.RegisterUser.as_view(), name='register_url'),
    path('register/success', views.RegisterSuccessView.as_view(), name='reg_success_url'),
    path('login', views.LoginUser.as_view(), name='login_url'),
    path('logout', views.logout_user, name='logout_url'),

    path('profile', views.ShowProfileView.as_view(), name='profile_url'),

    path('profile/change-pdata', views.ChangeProfileDataView.as_view(), name='change_pd_url'),
    path('profile/change-pdata/success', views.ChangeProfileDataSuccessView.as_view(), name='change_pd_success_url'),
    path('profile/change-password', views.ChangePasswordView.as_view(), name='change_pw_url'),
    path('profile/change-password/success', views.ChangePasswordSuccessView.as_view(), name='change_pw_success_url'),

    path('profile/history', views.UserTestHistoryListView.as_view(), name='history_url'),
    path('profile/history/<int:pk>', views.UserTestDetailView.as_view(), name='history_detail_url'),

    path('profile/stat', views.ShowStatView.as_view(), name='stat_url'),

]
