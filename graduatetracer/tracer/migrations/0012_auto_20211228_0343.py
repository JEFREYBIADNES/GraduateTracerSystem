# Generated by Django 3.2.7 on 2021-12-27 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tracer', '0011_rename_user_workexperiences_graduateuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workexperiences',
            name='experience_endDate',
        ),
        migrations.RemoveField(
            model_name='workexperiences',
            name='experience_startingDate',
        ),
    ]
