# Generated by Django 3.2 on 2021-05-04 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0011_auto_20210504_2320'),
    ]

    operations = [
        migrations.AddField(
            model_name='codefile',
            name='file_name',
            field=models.CharField(default='', max_length=100),
        ),
    ]
