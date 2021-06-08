from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class TaskAnswerType(models.TextChoices):
    CONSTANT_ANSWER = 'CA', _('Constant answer')
    VARIABLE_ANSWER = 'VA', _('Variable answer')


class CodeExecuteType(models.TextChoices):
    JUST_RUN = 'run', _('Only run source')
    BUILD_AND_RUN = 'build && run', _('Build binary, then run it')


class SolutionEventType(models.TextChoices):
    USER_TASK_SOLUTION = 'USER_SOLUTION', _('User solution to task')
    AUTHOR_TASK_VALIDATION = 'TASK_VALIDATION', _('Validation of authors task (all tests)')


class TaskGradingSystem(models.TextChoices):
    BINARY = 'BINARY', _('Accepted or failed')
    BINARY_FOR_EACH_TEST = 'BINARY TEST', _('1 Point for each test')
    N_POINTS_FOR_EACH_TEST = 'POINTS TEST', _('N points for each test')


class Language(models.TextChoices):
    GNU_ASM = 'ASM', _('GNU Assembly Language')
    GNU_C99 = 'C99', _('GNU GCC C99')
    GNU_C11 = 'C11', _('GNU GCC C11')
    GNU_CXX_11 = 'C++11', _('GNU G++ C++ 11')
    GNU_CXX_14 = 'C++14', _('GNU G++ C++ 14')
    GNU_CXX_17 = 'C++17', _('GNU G++ C++ 17')
    GNU_CXX_20 = 'C++20', _('GNU G++ C++ 20')
    PYTHON_2_7 = 'Python2', _('Python v2.7')
    PYTHON_3_9 = 'Python3', _('Python v3.9.4')
    JAVA_8 = 'Java8', _('Java 8')


lang_extension = {
    'ASM': 's',
    'C99': 'c',
    'C11': 'c',
    'C++11': 'cpp',
    'C++14': 'cpp',
    'C++17': 'cpp',
    'C++20': 'cpp',
    'Python2': 'py',
    'Python3': 'py',
    'Java8': 'java',
}


class Status(models.TextChoices):
    WAIT_FOR_CHECK = 'WAIT', _('Ожидается проверка')
    QUEUED = 'QUEUED', _('В очереди')
    IN_PROGRESS = 'IN PROGRESS', _('Проверяется')
    CHECK_FAILED = 'FAILED', _('Проверка не пройденя')
    CHECK_SUCCESS = 'SUCCESS', _('Проверка пройдена')


class Verdict(models.TextChoices):
    EMPTY_VERDICT = 'NO VERDICT', _('No verdict')
    WRONG_FILE_FORMAT = 'WRONG FILE FORMAT', _('Wrong format of file')
    FILE_TOO_BIG = 'FILE TOO BIG', _('File has too large size')
    BUILD_FAILED = 'BUILD FAILED', _('Build failed')
    RUNTIME_ERROR = 'RUNTIME ERROR', _('Runtime error')
    TIME_LIMIT_ERROR = 'TIME LIMIT ERROR', _('Time limit error')
    MEMORY_LIMIT_ERROR = 'MEMORY LIMIT ERROR', _('Memory limit error')
    WRONG_ANSWER = 'WRONG ANSWER', _('Wrong answer')
    PARTIAL_SOLUTION = 'PARTIAL SOLUTION', _('Partial solution')
    CORRECT_SOLUTION = 'CORRECT SOLUTION', _('Correct solution')


class CodeFile(models.Model):
    file = models.FileField(upload_to='code/%Y/%m/%d')
    language = models.TextField(choices=Language.choices)
    code = models.TextField(default='')
    file_name = models.CharField(default='', max_length=100)


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
    task_execute_type = models.TextField(choices=CodeExecuteType.choices, default=CodeExecuteType.BUILD_AND_RUN)
    solution_file = models.OneToOneField(to=CodeFile,
                                         on_delete=models.SET_NULL,
                                         null=True, blank=True,
                                         related_name='task')

    grading_system = models.TextField(choices=TaskGradingSystem.choices, default=TaskGradingSystem.BINARY)
    is_validated = models.BooleanField(default=False)

    # class Meta:
    #     abstract = True


class Test(models.Model):
    task = models.ForeignKey(AbstractTask, on_delete=models.CASCADE, related_name='tests')
    content = models.TextField()
    right_answer = models.TextField(blank=True)
    max_points = models.IntegerField(default=1)

    class Meta:
        ordering = ('id',)


class Solution(models.Model):
    author = models.ForeignKey(to=User, on_delete=models.CASCADE,
                               related_name='solutions',
                               blank=True)
    code_file = models.OneToOneField(to=CodeFile,
                                     on_delete=models.CASCADE,
                                     related_name='code_file')

    created = models.DateTimeField(default=datetime.now)

    status = models.TextField(choices=Status.choices,
                              default=Status.WAIT_FOR_CHECK)
    verdict = models.TextField(choices=Verdict.choices,
                               default=Verdict.EMPTY_VERDICT)
    verdict_text = models.TextField(blank=True,
                                    default='Посылка не проверена')

    task = models.ForeignKey(AbstractTask,
                             on_delete=models.CASCADE,
                             related_name='solutions',
                             default=None,
                             blank=True)
    node = models.IntegerField(default=1)

    event_type = models.TextField(choices=SolutionEventType.choices,
                                  default=SolutionEventType.USER_TASK_SOLUTION)
    points = models.IntegerField(default=0)
    cur_test = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created',)
