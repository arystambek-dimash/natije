# Generated by Django 5.0.1 on 2024-01-08 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_course_bought_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coursetheme',
            name='is_prime',
        ),
    ]
