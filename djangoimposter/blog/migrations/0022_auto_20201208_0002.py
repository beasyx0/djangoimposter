# Generated by Django 3.0.11 on 2020-12-08 05:02

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0021_auto_20201207_2233'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='post',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='blog_post_search__528e75_gin'),
        ),
    ]
