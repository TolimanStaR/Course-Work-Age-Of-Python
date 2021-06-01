# Generated by Django 3.2.3 on 2021-05-28 10:16

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('management', '0013_alter_codefile_language'),
        ('courses', '0016_rename_student_student_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('start_time', models.DateTimeField(default=datetime.datetime(2021, 5, 29, 13, 16, 57, 711634))),
                ('duration', models.DurationField(default=datetime.timedelta(0, 7200))),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='contests', to='courses.course')),
            ],
        ),
        migrations.CreateModel(
            name='ContestParticipant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='ContestSolution',
            fields=[
                ('solution_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='management.solution')),
            ],
            bases=('management.solution',),
        ),
        migrations.CreateModel(
            name='CourseSolution',
            fields=[
                ('solution_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='management.solution')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='solutions', to='courses.course')),
            ],
            bases=('management.solution',),
        ),
        migrations.CreateModel(
            name='CourseTask',
            fields=[
                ('abstracttask_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='management.abstracttask')),
                ('show_in_task_list', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='tasks', to='courses.course')),
            ],
            bases=('management.abstracttask',),
        ),
        migrations.AlterField(
            model_name='content',
            name='content_type',
            field=models.ForeignKey(limit_choices_to={'model__in': ('puretext', 'latex', 'codelisting', 'picture', 'videolink')}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.DeleteModel(
            name='PDF',
        ),
    ]