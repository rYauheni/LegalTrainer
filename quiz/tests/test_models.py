from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from quiz.models import Category, Question, Answer, Test, TestQuestion,UserTestModel, UserTestAnswer, UserTestResult


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Test Category')

    def test_category_creation(self):
        category = Category.objects.get(id=1)
        self.assertEqual(category.title, 'Test Category')
        self.assertEqual(category.slug, 'test-category')
        self.assertEqual(str(category), 'Test Category')
        self.assertEqual(category.get_absolute_url(), reverse('category_url',
                                                              kwargs={'slug_category': 'test-category'}))

    def test_category_ordering(self):
        category1 = Category.objects.create(title='Category 1')
        category2 = Category.objects.create(title='Category 2')
        category3 = Category.objects.create(title='Category 3')

        categories = Category.objects.all()
        self.assertEqual(categories[0], category1)
        self.assertEqual(categories[1], category2)
        self.assertEqual(categories[2], category3)


class QuestionModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Test Category')

    def test_question_creation(self):
        question = Question.objects.create(category=self.category, content='Test Question Content')
        self.assertEqual(question.category, self.category)
        self.assertEqual(question.content, 'Test Question Content')
        self.assertEqual(str(question), 'Test Question Content')

    def test_question_str_method(self):
        question = Question.objects.create(category=self.category, content='Another Test Question')
        self.assertEqual(str(question), 'Another Test Question')

    def test_question_category_relationship(self):
        question = Question.objects.create(category=self.category, content='Question with Category')
        self.assertEqual(question.category, self.category)

    def test_question_category_null(self):
        question = Question.objects.create(content='Question without Category')
        self.assertIsNone(question.category)

    def test_question_category_set_null_on_delete(self):
        question = Question.objects.create(category=self.category, content='Question to be deleted')
        category_id = self.category.id
        self.category.delete()
        question.refresh_from_db()
        self.assertIsNone(question.category)

    def test_question_ordering(self):
        question1 = Question.objects.create(category=self.category, content='Question 1')
        question2 = Question.objects.create(category=self.category, content='Question 2')
        question3 = Question.objects.create(category=self.category, content='Question 3')

        questions = Question.objects.all()
        self.assertEqual(questions[0], question1)
        self.assertEqual(questions[1], question2)
        self.assertEqual(questions[2], question3)


class TestModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Test Category')
        self.question = Question.objects.create(category=self.category, content='Test Question Content')

    def test_test_creation(self):
        test = Test.objects.create()
        self.assertIsNotNone(test.date)
        self.assertEqual(test.questions.count(), 0)

    def test_test_add_question(self):
        test = Test.objects.create()
        test.questions.add(self.question)
        self.assertEqual(test.questions.count(), 1)
        self.assertEqual(test.questions.first(), self.question)

    def test_test_remove_question(self):
        test = Test.objects.create()
        test.questions.add(self.question)
        test.questions.remove(self.question)
        self.assertEqual(test.questions.count(), 0)

    def test_test_date_auto_now_add(self):
        current_date = timezone.now().date()
        test = Test.objects.create()
        self.assertEqual(test.date, current_date)

    def test_test_category_included(self):
        test = Test.objects.create()
        test.questions.add(self.question)
        self.assertEqual(test.questions.first().category, self.category)


class TestQuestionModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Test Category')
        self.question = Question.objects.create(category=self.category, content='Test Question Content')

        self.test = Test.objects.create()

    def test_testquestion_creation(self):
        testquestion = TestQuestion.objects.create(test=self.test, question=self.question, order=1)
        self.assertEqual(testquestion.test, self.test)
        self.assertEqual(testquestion.question, self.question)
        self.assertEqual(testquestion.order, 1)

    def test_testquestion_ordering(self):
        testquestion1 = TestQuestion.objects.create(test=self.test, question=self.question, order=3)
        testquestion2 = TestQuestion.objects.create(test=self.test, question=self.question, order=1)
        testquestion3 = TestQuestion.objects.create(test=self.test, question=self.question, order=2)

        testquestions = TestQuestion.objects.order_by('order')
        self.assertEqual(testquestions[0], testquestion2)
        self.assertEqual(testquestions[1], testquestion3)
        self.assertEqual(testquestions[2], testquestion1)

    def test_testquestion_deletion_cascade(self):
        testquestion = TestQuestion.objects.create(test=self.test, question=self.question, order=1)
        test_id = self.test.id
        testquestion_id = testquestion.id

        self.test.delete()

        with self.assertRaises(TestQuestion.DoesNotExist):
            TestQuestion.objects.get(id=testquestion_id)


class UserTestModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Test Category')
        self.question = Question.objects.create(category=self.category, content='Test Question Content')

        self.test = Test.objects.create()

        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')

    def test_usertestmodel_creation(self):
        user_test_model = UserTestModel.objects.create(user=self.user, test=self.test, counter=1)
        self.assertEqual(user_test_model.user, self.user)
        self.assertEqual(user_test_model.test, self.test)
        self.assertEqual(user_test_model.counter, 1)

    def test_usertestmodel_default_counter(self):
        user_test_model = UserTestModel.objects.create(user=self.user, test=self.test)
        self.assertEqual(user_test_model.counter, 0)

    def test_usertestmodel_deletion_cascade(self):
        user_test_model = UserTestModel.objects.create(user=self.user, test=self.test, counter=1)
        user_id = self.user.id
        test_id = self.test.id

        self.user.delete()

        with self.assertRaises(UserTestModel.DoesNotExist):
            UserTestModel.objects.get(id=user_test_model.id)

        new_user = get_user_model().objects.create_user(username='newuser', password='newpassword')
        new_test = Test.objects.create()

        new_user_test_model = UserTestModel.objects.create(user=new_user, test=new_test, counter=1)

        new_test.delete()

        with self.assertRaises(UserTestModel.DoesNotExist):
            UserTestModel.objects.get(id=new_user_test_model.id)


class UserTestAnswerModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Test Category')
        self.question = Question.objects.create(category=self.category, content='Test Question Content')
        self.answer = Answer.objects.create(question=self.question, content='Test Answer Content', correctness=True)

        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.test = Test.objects.create()
        self.user_test_model = UserTestModel.objects.create(user=self.user, test=self.test, counter=1)

    def test_usertestanswer_creation(self):
        user_test_answer = UserTestAnswer.objects.create(user_test=self.user_test_model)
        user_test_answer.user_answers.add(self.answer)

        self.assertEqual(user_test_answer.user_test, self.user_test_model)
        self.assertEqual(user_test_answer.user_answers.count(), 1)
        self.assertEqual(user_test_answer.user_answers.first(), self.answer)

    def test_usertestanswer_remove_answer(self):
        user_test_answer = UserTestAnswer.objects.create(user_test=self.user_test_model)
        user_test_answer.user_answers.add(self.answer)

        user_test_answer.user_answers.remove(self.answer)

        self.assertEqual(user_test_answer.user_answers.count(), 0)

    def test_usertestanswer_clear_answers(self):
        user_test_answer = UserTestAnswer.objects.create(user_test=self.user_test_model)
        user_test_answer.user_answers.add(self.answer)

        user_test_answer.user_answers.clear()

        self.assertEqual(user_test_answer.user_answers.count(), 0)


class UserTestResultModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Test Category')
        self.question = Question.objects.create(category=self.category, content='Test Question Content')
        self.answer = Answer.objects.create(question=self.question, content='Test Answer Content', correctness=True)

        self.user = get_user_model().objects.create_user(username='testuser', password='testpassword')
        self.test = Test.objects.create()
        self.user_test_model = UserTestModel.objects.create(user=self.user, test=self.test, counter=1)

    def test_usertestresult_creation(self):
        user_test_result = UserTestResult.objects.create(user_test=self.user_test_model,
                                                         user_test_category=self.category)
        self.assertEqual(user_test_result.user_test, self.user_test_model)
        self.assertEqual(user_test_result.user_test_category, self.category)
        self.assertEqual(user_test_result.correct, 0)
        self.assertEqual(user_test_result.incorrect, 0)

    def test_usertestresult_update_counters(self):
        user_test_result = UserTestResult.objects.create(user_test=self.user_test_model,
                                                         user_test_category=self.category)

        user_test_result.correct += 1
        user_test_result.save()
        self.assertEqual(user_test_result.correct, 1)
        self.assertEqual(user_test_result.incorrect, 0)

        user_test_result.incorrect += 1
        user_test_result.save()
        self.assertEqual(user_test_result.correct, 1)
        self.assertEqual(user_test_result.incorrect, 1)
