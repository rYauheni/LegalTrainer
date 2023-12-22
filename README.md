# LegalTriner

[**LegalTrainer**](http://193.187.175.182:1336) is a modern online platform designed for legal education. The project offers users the opportunity to 
participate in engaging online tests covering various legal fields, track their progress, explore statistics, and 
compete in leaderboards.

## Project Goal
The goal of the project is to create a convenient tool that ensures effective legal education, focusing on 
interactivity, progress monitoring, and fostering a competitive spirit among users.

## Project Tasks
- Development of an interactive environment for legal education.
- Advancement of the testing system with diverse questions across various legal domains.
- Implementation of a mechanism for tracking and analyzing user progress.
- Integration of features to generate statistics on results and leaders.
- Ensuring user convenience through an intuitively understandable interface.

## Key Functional Features
- Conducting online tests covering different legal areas.
- Monitoring individual user progress.
- Providing statistics on results and achievements.
- Establishing a dynamic leaderboard to stimulate user engagement and competition.


You can try the application [here](http://193.187.175.182:1336).
___

## Technologies

[![Python](https://img.shields.io/badge/Python-3.10-%23FFD040?logo=python&logoColor=white&labelColor=%23376E9D)](https://www.python.org/downloads/release/python-31012/)
[![Django](https://img.shields.io/badge/Django-4.1-%232BA977?logo=django&logoColor=white&labelColor=%23092E20)](https://www.djangoproject.com/)

[![UnitTest](https://img.shields.io/badge/UnitTest-%23293133)](https://docs.python.org/3/library/unittest.html)

[![Gunicorn](https://img.shields.io/badge/Gunicorn-%23479946?logo=gunicorn&logoColor=white&labelColor=%23293133)](https://gunicorn.org/)
[![Nginx](https://img.shields.io/badge/Nginx-%23009639?logo=nginx&logoColor=white&labelColor=%23293133)](https://nginx.org/)

[![HTML](https://img.shields.io/badge/HTML-%23E44D25?logoColor=white&labelColor=%23293133&logo=html5)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![CSS](https://img.shields.io/badge/CSS-%23214CE5?logoColor=white&labelColor=%23293133&logo=css3)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![JavaScript](https://img.shields.io/badge/JavaScript-%23FFD83A?logoColor=white&labelColor=%23293133&logo=javascript)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-%232F6792?logoColor=white&labelColor=%23293133&logo=postgresql)](https://www.postgresql.org/)
[![SQLite](https://img.shields.io/badge/SQLite-%23003156?logoColor=white&labelColor=%23293133&logo=sqlite)](https://www.sqlite.org/)

[![Docker](https://img.shields.io/badge/Docker-%232496ED?logo=docker&logoColor=white&labelColor=%23293133)](https://www.docker.com/)

[![GitHub](https://img.shields.io/badge/GitHub-%23000000?logoColor=white&labelColor=%23293133&logo=github)](https://github.com/)

___

## Installation

Run the following commands to bootstrap your environment.

For Windows:

```commandline
git clone https://github.com/rYauheni/LegalTrainer.git

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

copy .env.template .env

```

For Linux:

```commandline
git clone https://github.com/rYauheni/LegalTrainer.git

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.template .env
```

___

## QuickStart for development

1. Determine the value of environment variables in the file `.env`


2. Run the app locally:
   
   for Windows:

   ```commandline
   python manage.py runserver 0.0.0.0:8000 --settings=LegalTrainer.settings.dev
   ```
   
   for Linux:

   ```commandline
   python3 manage.py runserver 0.0.0.0:8000 --settings=LegalTrainer.settings.dev
   ```
   
3. Run the app with gunicorn:

   for Windows&Linux:
   ```commandline
   gunicorn poker_stats_data.wsgi:application --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=LegalTrainer.settings.dev
   ```

4. Apply migrations:

   for Windows:

    ```commandline
    python manage.py migrate --settings=LegalTrainer.settings.dev
    ```

   for Linux:

   ```commandline
   python3 manage.py migrate --settings=LegalTrainer.settings.dev
   ```

5. Run tests:

   for Windows:

    ```commandline
    python manage.py test --settings=LegalTrainer.settings.dev
    ```

   for Linux:

   ```commandline
   python3 manage.py test --settings=LegalTrainer.settings.dev
   ```

___

## Launch for production

1. Determine the value of environment variables in the file `.env`


2. Run docker container with command:

    ```commandline
    docker compose up
    ```

3. Apply migrations:

    ```commandline
    docker compose exec web python manage.py migrate --noinput --settings=LegalTrainer.settings.prod
    ```

4. Create superuser

    ```commandline
    docker compose exec web python manage.py createsuperuser --settings=LegalTrainer.settings.prod
    ```

 ___

## Contributing

Bug reports and/or pull requests are welcome
___

## License

The app is dedicated to the public domain under the CC0 license