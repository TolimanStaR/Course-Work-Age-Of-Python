# Generated by Django 3.2 on 2021-04-27 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0004_solution_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solution',
            name='code',
            field=models.TextField(default=''),
        ),
    ]
