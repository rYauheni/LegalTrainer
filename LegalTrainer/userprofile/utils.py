import os
import uuid
import matplotlib.pyplot as plt
from django.conf import settings


def show_pie_histogram(correct: int, incorrect: int) -> str:
    if correct == 0 and incorrect == 0:
        return ''  #### добавить обработчик на случай если оба значения 0 (иначе вызывается исключение)
    vals = [correct, incorrect]
    labels = ['correct', 'incorrect']
    fig, ax = plt.subplots()
    ax.pie(vals, labels=labels)
    filename = str(uuid.uuid4()) + '.png'
    filepath = os.path.join('media', filename)
    print('filepath', filepath)
    plt.savefig(filepath, format='png')
    file_url = settings.MEDIA_URL + filename
    print('file_url', file_url)
    return file_url


def show_bar_histogram(vals: tuple, labels: tuple) -> str:
    fig, ax = plt.subplots()
    ax.bar(labels, vals)
    filename = str(uuid.uuid4()) + '.png'
    filepath = os.path.join('media', filename)
    print('filepath', filepath)
    plt.savefig(filepath, format='png')
    file_url = settings.MEDIA_URL + filename
    print('file_url', file_url)
    return file_url
