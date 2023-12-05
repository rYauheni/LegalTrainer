from django.test import TestCase, Client
from django.urls import reverse
from django.shortcuts import resolve_url

from quiz.models import Category
from quiz.views import ChooseCategoryView


class ChooseCategoryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.categories = [
            Category.objects.create(title='Category1', slug='category1'),
            Category.objects.create(title='Category2', slug='category2'),
        ]

    def test_get_categories(self):
        response = self.client.get(reverse('categories_list_url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/categories.html')

        expected_categories = list(Category.objects.all().order_by('title'))
        self.assertQuerysetEqual(response.context['categories'], expected_categories, ordered=False,
                                 transform=lambda x: x)

    def test_post_redirect(self):
        selected_category = self.categories[0]
        post_data = {selected_category.title: 'on'}
        response = self.client.post(reverse('categories_list_url'), post_data)

        self.assertRedirects(response, reverse('set_test_url', args=[selected_category.slug]))

