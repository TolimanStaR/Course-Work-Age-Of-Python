# Generated by Django 3.2 on 2021-05-04 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0010_auto_20210504_2236'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='test',
            options={'ordering': ('id',)},
        ),
        migrations.AddField(
            model_name='abstracttask',
            name='is_validated',
            field=models.BooleanField(default=False),
        ),
    ]
