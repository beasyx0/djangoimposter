# Generated by Django 3.0.11 on 2021-01-22 01:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0027_post_allow_comments'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='allow_comments',
        ),
    ]
