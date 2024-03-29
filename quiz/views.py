from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseNotFound
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView
from django.db.models import Max, Count

from random import shuffle, choice, choices

from .models import Category, Question, Answer, Test, TestQuestion, UserTestModel, UserTestAnswer, UserTestResult
from .forms import UserAnswersForm
from .utils import BarMixin, QUESTIONS_QUANTITY

from userprofile.models import UserStat

# Create your views here.


class IndexView(BarMixin, View):
    template_name = 'quiz/index.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        url = super().post(request)

        if 'choose_cat' in request.POST:
            url = reverse('categories_list_url')

        return redirect(url)


class AboutView(BarMixin, View):
    template_name = 'quiz/about.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        url = super().post(request)

        return redirect(url)


class ChooseCategoryView(BarMixin, View):
    def get(self, request):
        categories = Category.objects.all().order_by('title')
        return render(request, 'quiz/categories.html', context={'categories': categories})

    def post(self, request, *args, **kwargs):
        categories = Category.objects.all().order_by('title')
        url = super().post(request)

        for category in categories:
            if category.title in request.POST:
                slug_category = category.slug
                url = reverse('set_test_url', args=(slug_category, ))

        return redirect(url)


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'quiz/category.html'
    slug_url_kwarg = 'slug_category'
    context_object_name = 'category'


class SetTestView(BarMixin, View):
    def get(self, request, slug_category):
        category = Category.objects.get(slug=slug_category)
        qq = QUESTIONS_QUANTITY
        return render(request, 'quiz/start_test.html', context={'category': category, 'qq': qq})

    def post(self, request, slug_category, *args, **kwargs):
        url = super().post(request)
        if 'start' in request.POST:
            category = Category.objects.get(slug=slug_category)
            questions = Question.objects.filter(category=category)
            question_ids = [question.id for question in questions]
            shuffle(question_ids)

            if len(question_ids) >= QUESTIONS_QUANTITY:
                question_ids = question_ids[:QUESTIONS_QUANTITY]

            test = Test()
            test.save()

            for order, question_id in enumerate(question_ids):
                TestQuestion.objects.create(test=test, question_id=question_id, order=order)

            user_test = UserTestModel(user=request.user, test=test, counter=0)
            user_test.save()
            UserTestAnswer(user_test=user_test).save()

            user_test_questions = test.testquestion_set.order_by('order')
            for order, user_test_question in enumerate(user_test_questions):
                user_test_question.order = order
                user_test_question.save()

            counter = user_test.counter

            url = reverse('question_url', args=(counter,))
        elif 'cats' in request.POST:
            url = reverse('categories_list_url')

        return redirect(url)


class GetQuestionView(BarMixin, View):
    def get(self, request, q_number):
        user_tests = UserTestModel.objects.filter(user=request.user)
        last_number = len(user_tests) - 1
        user_test = user_tests[last_number]
        counter = user_test.counter
        test = Test.objects.get(usertestmodel=user_test)
        questions = test.testquestion_set.all().order_by('order')
        q_quantity = len(questions)
        question = questions[counter].question
        answers = Answer.objects.filter(question=question).order_by('?')

        user_test_answers = UserTestAnswer.objects.get(user_test=user_test)
        selected_answers = [str(answer.id) for answer in user_test_answers.user_answers.all()]

        form = UserAnswersForm(answers=answers, initial={'answers': selected_answers})

        if request.method == 'GET':
            return render(request, 'quiz/question.html', context={
                'user_test': user_test,
                'test': test,
                'questions': questions,
                'q_quantity': q_quantity,
                'question': question,
                'answers': answers,
                'counter': counter,
                'quantity': min(QUESTIONS_QUANTITY, len(questions)),
                'form': form,
            })

    def post(self, request, q_number):
        user_tests = UserTestModel.objects.filter(user=request.user)
        last_number = len(user_tests) - 1
        user_test = user_tests[last_number]
        counter = user_test.counter
        test = Test.objects.get(usertestmodel=user_test)
        questions = test.testquestion_set.all().order_by('order')
        question = questions[counter].question
        answers = Answer.objects.filter(question=question).order_by('?')

        form = UserAnswersForm(request.POST, answers=answers)

        form.full_clean()
        id_user_answers = form.cleaned_data
        user_test_answers = UserTestAnswer.objects.get(user_test=user_test)

        url = super().post(request)

        for old_answer in user_test_answers.user_answers.filter(question=question):
            user_test_answers.user_answers.remove(old_answer)

        for id_a in id_user_answers['answers']:
            user_test_answers.user_answers.add(Answer.objects.get(id=id_a))

        if 0 <= counter <= len(questions) - 1:
            if form.is_valid():
                if 'previous' in request.POST:
                    if user_test.counter > 0:
                        user_test.counter -= 1
                    user_test.save()
                    q_number = user_test.counter
                    url = reverse('question_url', args=(q_number,))
                elif 'next' in request.POST:
                    if user_test.counter < len(questions) - 1:
                        user_test.counter += 1
                    user_test.save()
                    q_number = user_test.counter
                    url = reverse('question_url', args=(q_number,))
                elif 'end' in request.POST:
                    url = reverse('result_url')

        else:
            raise ValueError(f'Counter value must be in range(0, {QUESTIONS_QUANTITY})')

        return redirect(url)


class ShowTestResultView(BarMixin, View):
    template_name = 'quiz/test_result.html'

    def get(self, request, *args, **kwargs):
        user_tests = UserTestModel.objects.filter(user=request.user)
        last_number = len(user_tests) - 1
        user_test = user_tests[last_number]
        user_test_questions = user_test.test.testquestion_set.order_by('order')
        category = user_test_questions[0].question.category

        user_answers = UserTestAnswer.objects.get(user_test=user_test)
        full_result = {}

        for user_test_question in user_test_questions:
            question = user_test_question.question
            answers = Answer.objects.filter(question=question)

            full_result.setdefault(question, {
                'answers': answers,
                'user_answers': [],
                'correct_answers': []
            })

            user_answers_list = user_answers.user_answers.filter(question=question)
            for u_answer in user_answers_list:
                full_result[question]['user_answers'].append(u_answer)

            if not full_result[question]['correct_answers']:
                correct_answers = Answer.objects.filter(question=question, correctness=True)
                for c_answer in correct_answers:
                    full_result[question]['correct_answers'].append(c_answer)

        quantity_questions = len(full_result)
        success_questions = 0

        for key in full_result:
            if sorted([answer.id for answer in full_result[key]['user_answers']]) == \
                    sorted([answer.id for answer in full_result[key]['correct_answers']]):
                success_questions += 1

        correctness_percent = round((100 / quantity_questions * success_questions), 2)

        user_test_result, created = UserTestResult.objects.get_or_create(
            user_test=user_test,
            user_test_category=category,
            correct=success_questions,
            incorrect=quantity_questions-success_questions
        )
        if created:
            user_test_result.save()

            user_stat, created = UserStat.objects.get_or_create(user=request.user, category=category)
            user_stat.correct += success_questions
            user_stat.incorrect += quantity_questions-success_questions
            user_stat.save()

        return render(request, self.template_name, context={
            'full_result': full_result,
            'user_test_result': user_test_result,
        })

    def post(self, request, *args, **kwargs):
        url = super().post(request)
        return redirect(url)
