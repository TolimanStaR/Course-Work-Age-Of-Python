from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class TaskAnswerType(models.TextChoices):
    CONSTANT_ANSWER = 'CA', _('Constant answer')
    VARIABLE_ANSWER = 'VA', _('Variable answer')


class TaskExecuteType(models.TextChoices):
    JUST_RUN = 'run', _('Only run source')
    BUILD_AND_RUN = 'build && run', _('Build binary, then run it')


class Language(models.TextChoices):
    GNU_ASM = 'ASM', _('GNU Assembly Language')
    GNU_C99 = 'C99', _('GNU GCC C99')
    GNU_C11 = 'C11', _('GNU GCC C11')
    GNU_CXX_11 = 'C++11', _('GNU G++ C++ 11')
    GNU_CXX_14 = 'C++14', _('GNU G++ C++ 14')
    GNU_CXX_17 = 'C++17', _('GNU G++ C++ 17')
    GNU_CXX_20 = 'C++20', _('GNU G++ C++ 20')


class CodeFile(models.Model):
    file = models.FileField(upload_to='code/%Y/%m/%d')
    language = models.TextField(choices=Language.choices)


class AbstractTask(models.Model):
    title = models.CharField(max_length=200)
    task_description = models.TextField()

    input_description = models.TextField()
    output_description = models.TextField()

    memory_limit_megabytes = models.IntegerField(default=128)
    time_limit_seconds = models.IntegerField(default=1)

    input_example = models.TextField()
    output_example = models.TextField()

    answer_type = models.TextField(choices=TaskAnswerType.choices)
    task_execute_type = models.TextField(choices=TaskExecuteType.choices)
    solution_file = models.OneToOneField(CodeFile, on_delete=models.SET_NULL, null=True)

    # class Meta:
    #     abstract = True


class Test(models.Model):
    task = models.ForeignKey(AbstractTask, on_delete=models.CASCADE)
    content = models.TextField()
    right_answer = models.TextField()


class Solution(models.Model):
    code_file = models.OneToOneField(CodeFile, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
