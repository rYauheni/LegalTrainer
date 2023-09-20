from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index_url'),

    path('categories', views.choose_category, name='categories_list_url'),
    path('categories/<slug:slug_category>', views.CategoryDetailView.as_view(), name='category_url'),


    path('quiz/categories/<slug:slug_category>', views.set_test, name='set_test_url'),
    path('quiz/question/<int:q_number>', views.get_question, name='question_url'),
    path('quiz/result/result', views.show_test_result, name='result_url')

]
