# Generated by Django 3.0.11 on 2021-01-22 20:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_user_avatar'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='avatar',
            new_name='user_avatar',
        ),
    ]
