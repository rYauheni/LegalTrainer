from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index_url'),

    path('categories', views.ChooseCategoryView.as_view(), name='categories_list_url'),
    path('categories/<slug:slug_category>', views.CategoryDetailView.as_view(), name='category_url'),


    path('quiz/categories/<slug:slug_category>', views.SetTestView.as_view(), name='set_test_url'),
    path('quiz/question/<int:q_number>', views.GetQuestionView.as_view(), name='question_url'),
    path('quiz/result/result', views.ShowTestResultView.as_view(), name='result_url')

]
