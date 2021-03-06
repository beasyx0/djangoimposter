# Generated by Django 3.0.11 on 2020-12-08 03:33

import django.contrib.postgres.search
from django.db import migrations
from django.contrib.postgres.operations import TrigramExtension

class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0020_post_search_vector'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(editable=False, null=True),
        ),
        TrigramExtension(),
    ]
