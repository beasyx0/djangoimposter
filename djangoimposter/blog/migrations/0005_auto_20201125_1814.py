# Generated by Django 3.0.11 on 2020-11-25 23:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0004_auto_20201125_1807'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='newsletters',
            options={'ordering': ['-date'], 'verbose_name_plural': 'Newsletters'},
        ),
    ]
