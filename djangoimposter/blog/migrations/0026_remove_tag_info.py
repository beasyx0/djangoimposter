# Generated by Django 3.0.11 on 2021-01-01 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0025_auto_20210101_1414'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='info',
        ),
    ]
