# Generated by Django 4.1.1 on 2022-09-27 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracer', '0053_delete_systemuser_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='graduate',
            field=models.BooleanField(default=False),
        ),
    ]