# Generated by Django 3.0.5 on 2020-10-22 11:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('collect', '0005_auto_20201022_1127'),
    ]

    operations = [
        migrations.RenameField(
            model_name='idiomraw',
            old_name='parser_1_info',
            new_name='parser_info',
        ),
        migrations.RemoveField(
            model_name='idiomraw',
            name='parser_2_info',
        ),
        migrations.AlterField(
            model_name='idiomraw',
            name='main_html',
            field=models.TextField(default=None, null=True),
        ),
    ]
