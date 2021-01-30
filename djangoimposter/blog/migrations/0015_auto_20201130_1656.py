# Generated by Django 3.0.11 on 2020-11-30 21:56

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0014_auto_20201130_1651'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='bookmarked',
        ),
        migrations.AddField(
            model_name='post',
            name='bookmarked',
            field=models.ManyToManyField(blank=True, null=True, related_name='bookmarked_posts', to=settings.AUTH_USER_MODEL),
        ),
    ]