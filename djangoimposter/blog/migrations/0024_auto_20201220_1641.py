# Generated by Django 3.0.11 on 2020-12-20 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0023_auto_20201209_2223'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='newsletters',
        ),
        migrations.AddField(
            model_name='post',
            name='newsletters',
            field=models.ManyToManyField(blank=True, null=True, related_name='posts', to='blog.NewsletterSignup'),
        ),
    ]
