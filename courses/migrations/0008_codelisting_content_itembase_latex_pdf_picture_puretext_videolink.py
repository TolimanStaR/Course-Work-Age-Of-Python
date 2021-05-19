# Generated by Django 3.2 on 2021-05-19 13:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('courses', '0007_auto_20210518_1753'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemBase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('uploaded', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itembase_related_content', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CodeListing',
            fields=[
                ('itembase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='courses.itembase')),
                ('code', models.TextField(blank=True)),
            ],
            bases=('courses.itembase',),
        ),
        migrations.CreateModel(
            name='LaTeX',
            fields=[
                ('itembase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='courses.itembase')),
                ('file', models.FileField(upload_to='course_LaTeX_files/')),
            ],
            bases=('courses.itembase',),
        ),
        migrations.CreateModel(
            name='PDF',
            fields=[
                ('itembase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='courses.itembase')),
                ('file', models.FileField(upload_to='course_pdf_files/')),
            ],
            bases=('courses.itembase',),
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('itembase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='courses.itembase')),
                ('image', models.ImageField(upload_to='course_content_images/')),
            ],
            bases=('courses.itembase',),
        ),
        migrations.CreateModel(
            name='PureText',
            fields=[
                ('itembase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='courses.itembase')),
                ('text', models.TextField(blank=True)),
            ],
            bases=('courses.itembase',),
        ),
        migrations.CreateModel(
            name='VideoLink',
            fields=[
                ('itembase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='courses.itembase')),
                ('url', models.URLField()),
            ],
            bases=('courses.itembase',),
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(limit_choices_to={'model__in': ('puretext', 'pdf', 'latex', 'codelisting', 'picture', 'videolink')}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='content_list', to='courses.module')),
            ],
        ),
    ]
