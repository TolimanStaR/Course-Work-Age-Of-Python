# Generated by Django 3.2 on 2021-04-19 17:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('task_description', models.TextField()),
                ('input_description', models.TextField()),
                ('output_description', models.TextField()),
                ('memory_limit_megabytes', models.IntegerField(default=128)),
                ('time_limit_seconds', models.IntegerField(default=1)),
                ('input_example', models.TextField()),
                ('output_example', models.TextField()),
                ('answer_type', models.TextField(choices=[('CA', 'Constant answer'), ('VA', 'Variable answer')])),
                ('task_execute_type', models.TextField(choices=[('run', 'Only run source'), ('build && run', 'Build binary, then run it')])),
            ],
        ),
        migrations.CreateModel(
            name='CodeFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='code/%Y/%m/%d')),
                ('language', models.TextField(choices=[('ASM', 'GNU Assembly Language'), ('C99', 'GNU GCC C99'), ('C11', 'GNU GCC C11'), ('C++11', 'GNU G++ C++ 11'), ('C++14', 'GNU G++ C++ 14'), ('C++17', 'GNU G++ C++ 17'), ('C++20', 'GNU G++ C++ 20')])),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('right_answer', models.TextField()),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='management.abstracttask')),
            ],
        ),
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('code_file', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='management.codefile')),
            ],
        ),
        migrations.AddField(
            model_name='abstracttask',
            name='solution_file',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='management.codefile'),
        ),
    ]
