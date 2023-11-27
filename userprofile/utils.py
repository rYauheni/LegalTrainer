import os
import uuid
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

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

FONTS = {
    'fontproperties': FontProperties(family='Montserrat', size=16),
    'color': '#333333'
}


def show_pie_histogram(correct: int, incorrect: int, is_label: bool) -> str:
    if correct == 0 and incorrect == 0:
        placeholder_image_path = static('img/his_placeholder.png')
        return placeholder_image_path
    vals = [correct, incorrect]
    if is_label:
        labels = ['Верно', 'Неверно']
    else:
        labels = None
    colors = ['#03C03C', '#D53E07']
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.pie(
        vals,
        labels=labels,
        colors=colors,
        autopct='%2.1f%%',
        textprops=FONTS,
        wedgeprops=dict(width=0.6, )
    )

    filename = str(uuid.uuid4()) + '.png'
    filepath = os.path.join('media', filename)
    plt.savefig(filepath, format='png', bbox_inches='tight')
    plt.close()
    file_url = settings.MEDIA_URL + filename
    return file_url


def show_bar_histogram(vals: tuple, labels: tuple) -> str:
    fig, ax = plt.subplots(figsize=(14, 6), dpi=100)
    colors = ['#6c55e7', '#7754da', '#8353cc', '#8e50bc', '#9a50af', '#a44ea2', '#ad4c96', '#b24c91', '#af4c94',
              '#a64d9f', '#9d4fac', '#9150b9', '#9150b9', '#8152cd']
    bars = ax.bar(
        labels,
        vals,
        color=colors
    )
    ax.set_xticklabels(labels, rotation=45, ha='right', fontdict=FONTS)

    ax.spines['left'].set_color('#333333')
    ax.spines['bottom'].set_color('#333333')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='y', labelsize=14, colors='#333333')

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.0f}',
                ha='center', va='bottom', fontdict=FONTS)

    filename = str(uuid.uuid4()) + '.png'
    filepath = os.path.join('media', filename)
    plt.savefig(filepath, format='png', bbox_inches='tight')
    plt.close()
    file_url = settings.MEDIA_URL + filename
    return file_url
