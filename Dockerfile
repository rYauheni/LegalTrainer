FROM python:3.10-alpine3.15

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


RUN pip install --upgrade pip

WORKDIR /app
RUN mkdir static
RUN mkdir media

COPY . /app

RUN pip install -r requirements.txt

EXPOSE 8000

RUN python manage.py collectstatic --noinput --settings=LegalTrainer.settings.prod
