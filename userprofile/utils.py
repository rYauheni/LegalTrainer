import os
import uuid
import matplotlib
import matplotlib.pyplot as plt
from django.conf import settings
from django.templatetags.static import static

matplotlib.use('agg')

USERNAME_VALIDATION = {
    'min_length': 4,
    'max_length': 20,
    'content': r'^[a-zA-Z0-9]+$'  # only Latin letters and digits
}

PASSWORD_VALIDATION = {
    'min_length': 8,
    'max_length': 20,
    'content': r'^[a-zA-Z0-9]+$',  # only Latin letters and digits
    'requirements': r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$'  # at least one uppercase, one lowercase letter and one digit
}


def show_pie_histogram(correct: int, incorrect: int) -> str:
    if correct == 0 and incorrect == 0:
        placeholder_image_path = static('img/his_placeholder.png')
        return placeholder_image_path  #### добавить обработчик на случай если оба значения 0 (иначе вызывается исключение)
    vals = [correct, incorrect]
    labels = ['correct', 'incorrect']
    fig, ax = plt.subplots()
    ax.pie(vals, labels=labels)
    filename = str(uuid.uuid4()) + '.png'
    filepath = os.path.join('media', filename)
    plt.savefig(filepath, format='png')
    plt.close()
    file_url = settings.MEDIA_URL + filename
    return file_url


def show_bar_histogram(vals: tuple, labels: tuple) -> str:
    fig, ax = plt.subplots()
    ax.bar(labels, vals)
    filename = str(uuid.uuid4()) + '.png'
    filepath = os.path.join('media', filename)
    plt.savefig(filepath, format='png')
    plt.close()
    file_url = settings.MEDIA_URL + filename
    return file_url
