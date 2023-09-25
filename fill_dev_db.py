def create_categories(category):
    for i in 'ABCDEFGHIJ':
        category.objects.create(title=f'category_{i}')
    print('\033[34m', 'Categories created successfully.')


def create_questions(category, question):
    categories = category.objects.all()
    for c in categories:
        for i in range(1, 25):
            question.objects.create(category=c, content=f'{c.title[9]}_question_{i}')
    print('\033[34m', 'Questions created successfully.')


def create_answers(question, answer):
    from random import randint
    questions = question.objects.all()
    for q in questions:
        qn = int(q.content[11:])
        for i in range(1, randint(3, 7)):
            correct = False
            if (qn % 2 == 0 and i % 2 == 0) or (qn % 2 != 0 and i % 2 != 0):
                correct = True
            answer.objects.create(question=q, content=f'{q.category.title[9]}_q{qn}_answer_{i}', correctness=correct)
    print('\033[34m', 'Answers created successfully.')


def fill_db():
    from quiz.models import Category, Question, Answer
    create_categories(category=Category)
    create_questions(category=Category, question=Question)
    create_answers(question=Question, answer=Answer)
    print('\033[32m', 'Database filled successfully.')
    print('\033[0m')
