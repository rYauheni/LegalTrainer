from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index_url'),
    path('register', views.RegisterUser.as_view(), name='register_url'),
    path('register/success', views.get_register_success, name='reg_success_url'),
    path('login', views.LoginUser.as_view(), name='login_url'),
    path('logout', views.logout_user, name='logout_url'),
    path('categories', views.CategoryListView.as_view(), name='categories_list_url'),
    path('categories/<slug:slug_category>', views.CategoryDetailView.as_view(), name='category_url'),


    path('quiz/<slug:slug_category>', views.set_test, name='set_test_url'),
    path('quiz/question/<int:q_number>', views.get_question, name='question_url'),
    path('quiz/result/result', views.show_test_result, name='result_url')

]
