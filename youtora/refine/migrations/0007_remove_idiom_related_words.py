# Generated by Django 3.0.5 on 2020-10-23 02:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('refine', '0006_auto_20201023_0201'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='idiom',
            name='related_words',
        ),
    ]
