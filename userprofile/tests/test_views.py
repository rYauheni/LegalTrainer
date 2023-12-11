from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

from unittest.mock import patch

from quiz.models import Test, UserTestModel, UserTestResult, Category, Question, TestQuestion, Answer, UserTestAnswer
from userprofile.models import UserStat

from userprofile.views import UserTestHistoryListView


class RegisterUserTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_user_invalid_form(self):
        post_data = {
            'username': 'usr',
            'email': 'usr.mail',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'captcha': ''
        }

        response = self.client.post(reverse('register_url'), post_data)
        self.assertEqual(response.status_code, 200)

        user_model = get_user_model()
        with self.assertRaises(user_model.DoesNotExist):
            user_model.objects.get(username='testuser')

        self.assertFalse(response.wsgi_request.user.is_authenticated)

        self.assertTemplateUsed(response, 'userprofile/register.html')


class RegisterSuccessViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get(self):
        response = self.client.get(reverse('reg_success_url'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofile/reg_success.html')


class LoginUserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.login_url = reverse('login_url')

    def test_login_user_success(self):
        post_data = {
            'username': 'testuser',
            'password': 'testpassword',
        }

        response = self.client.post(self.login_url, post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

        self.assertRedirects(response, reverse('index_url'))

    def test_login_user_invalid_credentials(self):
        post_data = {
            'username': 'testuser',
            'password': 'wrongpassword',
        }

        response = self.client.post(self.login_url, post_data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Логин или пароль введены неверно.')


class LogoutUserTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.login_url = reverse('login_url')
        self.logout_url = reverse('logout_url')

    def test_logout_user(self):
        self.client.login(username='testuser', password='testpassword')

        self.assertTrue(self.client.session['_auth_user_id'])

        response = self.client.get(self.logout_url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['user'].is_authenticated)

        self.assertRedirects(response, self.login_url)

        self.assertNotIn('_auth_user_id', self.client.session)


class ShowProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_profile(self):
        User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('profile_url'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'userprofile/profile.html')

    def test_post_change_pd(self):
        User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(reverse('profile_url'), {'change_pd': 'on'})

        self.assertRedirects(response, reverse('change_pd_url'))

    def test_post_change_pw(self):
        User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        response = self.client.post(reverse('profile_url'), {'change_pw': 'on'})

        self.assertRedirects(response, reverse('change_pw_url'))


class ChangeProfileDataViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_change_profile_data(self):
        User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('change_pd_url'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'userprofile/change_profile_data.html')

    def test_post_change_profile_data_success(self):
        user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        post_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass',
        }
        response = self.client.post(reverse('change_pd_url'), post_data)

        self.assertRedirects(response, reverse('change_pd_success_url'))

        user.refresh_from_db()

        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'newuser@example.com')

    def test_post_change_profile_data_invalid_password(self):
        User.objects.create_user(username='testuser', password='testpass', email='testuser@example.com')
        self.client.login(username='testuser', password='testpass')

        post_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse('change_pd_url'), post_data)

        form = response.context['form']
        self.assertTrue('password' in form.errors)

        user = User.objects.get(username='testuser')

        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'testuser@example.com')

        self.assertTemplateUsed(response, 'userprofile/change_profile_data.html')


class ChangeProfileDataSuccessViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_change_profile_data_success(self):
        get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('change_pd_success_url'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'userprofile/change_pd_success.html')


class ChangePasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_change_password(self):
        get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        response = self.client.get(reverse('change_pw_url'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'userprofile/change_password.html')

        self.assertIsInstance(response.context['form'], PasswordChangeForm)

    def test_post_change_password_success(self):
        # Создаем пользователя для теста
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        post_data = {
            'old_password': 'testpass',
            'new_password1': 'Newtestpass1',
            'new_password2': 'Newtestpass1',
        }
        response = self.client.post(reverse('change_pw_url'), post_data)

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(response, reverse('change_pw_success_url'))

        user.refresh_from_db()
        self.assertTrue(user.check_password('Newtestpass1'))

    def test_post_change_password_invalid_data(self):
        user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        post_data = {
            'old_password': 'wrongpass',
            'new_password1': 'newtestpass',
            'new_password2': 'newtestpass',
        }
        response = self.client.post(reverse('change_pw_url'), post_data)

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'userprofile/change_password.html')

        form = response.context['form']
        self.assertTrue('old_password' in form.errors)

        user.refresh_from_db()
        self.assertTrue(user.check_password('testpass'))


class ChangePasswordSuccessViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_change_password_success(self):
        response = self.client.get(reverse('change_pw_success_url'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'userprofile/change_pw_success.html')


class UserTestHistoryListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_get_user_test_history_list(self):
        test1 = Test.objects.create()
        test2 = Test.objects.create()

        UserTestModel.objects.create(user=self.user, test=test1)
        UserTestModel.objects.create(user=self.user, test=test2)
        UserTestModel.objects.create(user=self.user, test=test1)

        response = self.client.get(reverse('history_url'))  # Замените 'history_url' на реальный URL

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'userprofile/history.html')

        user_tests = response.context['user_tests']
        self.assertIsInstance(user_tests, dict)
        self.assertGreater(len(user_tests), 0)
        for user_test, test_data in user_tests.items():
            self.assertIn('is_finished', test_data)
            self.assertIn('category', test_data)
            self.assertIn('correct', test_data)
            self.assertIn('incorrect', test_data)
            self.assertIn('number', test_data)


class UserTestDetailViewTest(TestCase):
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

        self.user_test_result = UserTestResult.objects.create(
            user_test=self.user_test,
            user_test_category=self.category,
            correct=1,
            incorrect=1
        )

    def test_get_user_test_detail(self):
        response = self.client.get(reverse('history_detail_url', kwargs={'pk': self.user_test.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofile/history_detail.html')

        user_test_result = response.context['user_test_result']
        full_user_test_result = response.context['full_user_test_result']

        self.assertIsInstance(user_test_result, UserTestResult)
        self.assertIsInstance(full_user_test_result, dict)

        self.assertEqual(len(full_user_test_result), len(self.questions))
        for question, data in full_user_test_result.items():
            self.assertIn(question, self.questions)
            self.assertIn('answers', data)
            self.assertIn('user_answers', data)
            self.assertIn('correct_answers', data)

        for question, data in full_user_test_result.items():
            self.assertIn(question, self.questions)

        for question, data in full_user_test_result.items():
            user_answers = data['user_answers']
            expected_answers = self.user_test_answers.user_answers.filter(question=question)
            self.assertEqual(set(user_answers), set(expected_answers))


class ShowStatViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        self.category1 = Category.objects.create(title='Category 1', slug='category-1')
        self.category2 = Category.objects.create(title='Category 2', slug='category-2')

        self.test1 = Test.objects.create()
        self.test2 = Test.objects.create()

        self.user_test1 = UserTestModel.objects.create(user=self.user, test=self.test1, counter=0)
        self.user_test2 = UserTestModel.objects.create(user=self.user, test=self.test2, counter=0)

        UserStat.objects.create(user=self.user, category=self.category1, correct=5, incorrect=2)
        UserStat.objects.create(user=self.user, category=self.category2, correct=4, incorrect=3)

    @patch('userprofile.views.cleanup_old_images')
    def test_show_stat_view(self, mock_cleanup):
        url = reverse('stat_url')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'userprofile/stat.html')

        self.assertEqual(response.context['total_tests'], 2)
        self.assertEqual(response.context['total_questions'], 14)

        mock_cleanup.assert_called_once()


class LeaderBoardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

    def test_leaderboard_view(self):
        self.category1 = Category.objects.create(title='Category 1', slug='category-1')

        UserStat.objects.create(user=self.user1, category=self.category1, correct=10, incorrect=5)
        UserStat.objects.create(user=self.user2, category=self.category1, correct=8, incorrect=2)

        response = self.client.get(reverse('leaderboard_url'))

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'userprofile/leaderboard.html')

        self.assertIn('top_10', response.context)
        self.assertIn('user_in_top', response.context)
        self.assertIn('user_result', response.context)

        self.assertIn(str(self.user1), response.context['top_10'])
        self.assertIn(str(self.user2), response.context['top_10'])

        user1_result = response.context['top_10'][str(self.user1)]
        user2_result = response.context['top_10'][str(self.user2)]

        self.assertEqual(user1_result['quantity'], 15)
        self.assertEqual(user1_result['correctness'], 66.67)
        self.assertEqual(user1_result['points'], 667)

        self.assertEqual(user2_result['quantity'], 10)
        self.assertEqual(user2_result['correctness'], 80)
        self.assertEqual(user2_result['points'], 640)
