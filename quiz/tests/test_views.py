from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from quiz.models import Category, Question, Test, TestQuestion, UserTestModel, UserTestAnswer, Answer


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get(reverse('index_url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/index.html')

    def test_post_redirect_to_categories_list(self):
        post_data = {'choose_cat': 'on'}
        response = self.client.post(reverse('index_url'), post_data)

        self.assertRedirects(response, reverse('categories_list_url'))


class AboutViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get(reverse('about_url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/about.html')


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


class SetTestViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Category.objects.create(title='Category1', slug='category1')

        # Создаем достаточное количество вопросов для категории
        for i in range(10):
            Question.objects.create(category=self.category, content=f'Question {i}')

    def test_get(self):
        response = self.client.get(reverse('set_test_url', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/start_test.html')

    def test_post_start_test(self):
        post_data = {'start': 'on'}
        response = self.client.post(reverse('set_test_url', args=[self.category.slug]), post_data)

        self.assertRedirects(response, reverse('question_url', args=[0]))


class GetQuestionViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Category.objects.create(title='Category1', slug='category1')

        self.test = Test.objects.create()
        self.questions = [
            Question.objects.create(category=self.category, content=f'Question {i}')
            for i in range(5)  # Замените на нужное количество вопросов
        ]
        for order, question in enumerate(self.questions):
            TestQuestion.objects.create(test=self.test, question=question, order=order)

        self.answers = [
            Answer.objects.create(
                question=self.questions[0],
                content=f'Answer {i}',
                correctness=True if i % 2 == 0 else False
            )
            for i in range(4)  # Замените на нужное количество ответов
        ]

        self.user_test = UserTestModel.objects.create(user=self.user, test=self.test, counter=0)
        self.user_test_answers = UserTestAnswer.objects.create(user_test=self.user_test)

    def test_get(self):
        response = self.client.get(reverse('question_url', args=[0]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/question.html')

    def test_post_previous(self):
        post_data = {'previous': 'on', 'answers': [str(answer.id) for answer in self.answers]}

        response = self.client.post(reverse('question_url', args=[0]), post_data)

        self.assertRedirects(response, reverse('question_url', args=[0]))

    def test_post_next(self):
        post_data = {'next': 'on', 'answers': [str(answer.id) for answer in self.answers]}
        response = self.client.post(reverse('question_url', args=[0]), post_data)

        self.assertRedirects(response, reverse('question_url', args=[1]))

    def test_post_end(self):
        post_data = {'end': 'on', 'answers': [str(answer.id) for answer in self.answers]}
        response = self.client.post(reverse('question_url', args=[0]), post_data)

        self.assertRedirects(response, reverse('result_url'))


class ShowTestResultViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category = Category.objects.create(title='Category1', slug='category1')

        self.test = Test.objects.create()
        self.questions = [
            Question.objects.create(category=self.category, content=f'Question {i}')
            for i in range(5)
        ]
        for order, question in enumerate(self.questions):
            TestQuestion.objects.create(test=self.test, question=question, order=order)

        self.answers = [
            Answer.objects.create(
                question=question,
                content=f'Answer {i}',
                correctness=True if i % 2 == 0 else False
            )
            for question in self.questions
            for i in range(4)
        ]

        self.user_test = UserTestModel.objects.create(user=self.user, test=self.test, counter=0)
        self.user_test_answers = UserTestAnswer.objects.create(user_test=self.user_test)
        for question in self.questions:
            self.user_test_answers.user_answers.add(Answer.objects.filter(question=question).first())

    def test_get_show_test_result(self):
        response = self.client.get(reverse('result_url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'quiz/test_result.html')
