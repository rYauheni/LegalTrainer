# Generated by Django 4.1.5 on 2023-03-08 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0011_rename_answer_testanswer_answers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertestmodel',
            name='answers',
        ),
        migrations.AddField(
            model_name='usertestmodel',
            name='answers',
            field=models.ManyToManyField(blank=True, to='quiz.answer'),
        ),
    ]
