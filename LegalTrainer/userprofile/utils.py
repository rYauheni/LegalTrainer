import os
import uuid
import matplotlib.pyplot as plt
from django.conf import settings


def show_pie_histogram(correct=0, incorrect=0):
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
