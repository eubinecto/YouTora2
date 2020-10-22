# Generated by Django 3.0.5 on 2020-10-22 05:12

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('collect', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='idiomraw',
            name='main_html',
        ),
        migrations.AddField(
            model_name='idiomraw',
            name='idiom_info',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=None),
        ),
    ]