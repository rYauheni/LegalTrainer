from django.test import TestCase
from django.contrib.auth import get_user_model
from userprofile.models import UserStat, Category


class UserStatModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.category = Category.objects.create(title='Test Category')

    def test_userstat_creation(self):
        user_stat = UserStat.objects.create(user=self.user, category=self.category)
        self.assertEqual(user_stat.user, self.user)
        self.assertEqual(user_stat.category, self.category)
        self.assertEqual(user_stat.correct, 0)
        self.assertEqual(user_stat.incorrect, 0)

    def test_userstat_update_counters(self):
        user_stat = UserStat.objects.create(user=self.user, category=self.category)

        user_stat.correct += 1
        user_stat.save()
        self.assertEqual(user_stat.correct, 1)
        self.assertEqual(user_stat.incorrect, 0)

        user_stat.incorrect += 1
        user_stat.save()
        self.assertEqual(user_stat.correct, 1)
        self.assertEqual(user_stat.incorrect, 1)
