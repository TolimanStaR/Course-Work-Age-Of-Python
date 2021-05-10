# Generated by Django 3.2 on 2021-04-27 18:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('management', '0002_auto_20210427_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='solution',
            name='task',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to='management.abstracttask'),
        ),
        migrations.AlterField(
            model_name='solution',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='solutions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='solution',
            name='code_file',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='code_file', to='management.codefile'),
        ),
        migrations.AlterField(
            model_name='test',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tests', to='management.abstracttask'),
        ),
    ]