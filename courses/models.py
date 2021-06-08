import datetime

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

from management.fields import OrderField

from management.models import AbstractTask, Test, Solution, Language, Status


class Channel(models.Model):
    owner = models.OneToOneField(to=User,
                                 on_delete=models.DO_NOTHING)
    # owner of the channel

    title = models.CharField(max_length=100)
    # title of the channel

    slug = models.SlugField(unique=True, max_length=100, default='')
    # unique link to channel

    background_color = models.CharField(max_length=10, blank=True)
    # background color of the channel main page

    preview_image = models.ImageField(upload_to='channel_preview_images/')
    # On the channel list / boards

    background_image = models.ImageField(blank=True, upload_to='channel_background_images/')
    # background image at the back of the channel main page

    cover_image = models.ImageField(upload_to='channel_cover_images/', blank=True)
    # like 1440x900 img at the top of the channel description

    channel_description = models.TextField(blank=True)
    # description of channel at the top of channel page

    owner_full_name = models.CharField(max_length=200)
    # full name of channel owner

    owner_photo = models.ImageField(upload_to='channel_owner_photos/')
    # real photo of channel owner

    owner_interview = models.TextField()
    # little interview about channel owner

    subscribers = models.ManyToManyField(to=User, related_name='subscribes', blank=True)
    # many-to-may relationship between users and channels implementing subscribe system


class CourseThemes(models.TextChoices):
    ARITHMETIC = 'ARITHMETIC', _('Арифметика')
    MATH = 'MATH', _('Математика')
    ALGEBRA = 'ALGEBRA', _('Алгебра')
    CALCULUS = 'CALCULUS', _('Математический анализ')
    T_W_I_M_S = 'T_W_I_M_S', _('Теория вероятностей и математическая статистика')
    DISCRETE_MATH = 'DISCRETE_MATH', _('Дискретная математика')
    NUMBER_THEORY = 'NUMBER_THEORY', _('Теория чисел')
    WEB = 'WEB', _('Web-Программирование')
    DATA_SCIENCE = 'DATA_SCIENCE', _('Data science / Наука о данных')
    NEURAL_NET_MACHINE_LEARNING = 'NEURAL_MACHINE', _('Нейронные сети и машинное обучение')
    ALGORITHMS = 'ALGORITHMS', _('Алгоритмы и структуры данных')
    MOBILE = 'MOBILE', _('Мобильная разработка')
    TESTING = 'TESTING', _('Тестирование')
    DEV_OPS = 'DEV_OPS', _('DevOps')
    MANAGEMENT = 'MANAGEMENT', _('Менеджмент')
    BUSINESS = 'BUSINESS', _('Бизнес')
    FOREIGN_LANGUAGES = 'FOREIGN_LANGUAGES', _('Иностранные языки')
    ABSTRACT = 'NONE', _('Без направления')


class Course(models.Model):
    owner = models.ForeignKey(to=User,
                              on_delete=models.DO_NOTHING,
                              related_name='own_courses',
                              default=None)
    # owner of the channel->course

    channel = models.ForeignKey(to=Channel,
                                on_delete=models.CASCADE,
                                related_name='courses',
                                null=True,
                                default=None)
    # channel where course implemented

    title = models.CharField(max_length=150)
    # title of the course

    slug = models.SlugField(unique=True, max_length=100, default='')
    # course unique identifier in url

    description = models.TextField(default='', blank=True)
    # description at the course page

    theme = models.TextField(choices=CourseThemes.choices, default=CourseThemes.ABSTRACT)
    # course theme / tag

    show_course_in_channel_page = models.BooleanField(default=False)
    # should course be in channel main page

    created = models.DateTimeField(default=now, editable=False)
    # time of course creation

    preview_picture = models.ImageField(upload_to='course_preview_images/', blank=True)
    # preview image at the courses list

    main_picture = models.ImageField(upload_to='course_main_pictures/', blank=True)

    # picture at the course main page

    def get_theme(self):
        d = dict()
        for elem in CourseThemes.choices:
            d[elem[0]] = elem[1]
        return d[self.theme]

    ###### students = models.ManyToManyField(to=User, related_name='courses', blank=True)

    # query of students at the course

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title


class Student(models.Model):
    course = models.ForeignKey(to=Course, related_name='students', on_delete=models.DO_NOTHING)
    user = models.ForeignKey(to=User, related_name='courses', on_delete=models.DO_NOTHING)
    created = models.DateTimeField(default=now, editable=False)
    cur_module = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ('-created',)


class Module(models.Model):
    course = models.ForeignKey(to=Course,
                               on_delete=models.CASCADE,
                               related_name='modules')
    # heading course of module

    title = models.CharField(max_length=200)
    # title of the module

    description = models.TextField(blank=True)
    # some information about module content

    order = OrderField(blank=True, for_fields=['course'], default=1)

    # just number of course

    def __str__(self):
        return f'Модуль {self.order}: {self.title}'

    class Meta:
        ordering = ('order',)


class ModuleDescriptionListElement(models.Model):
    module = models.ForeignKey(to=Module,
                               on_delete=models.CASCADE,
                               related_name='list_elements')
    text = models.TextField(blank=True)

    class Meta:
        ordering = ('-id',)


class CourseDescriptionBlockImagePosition(models.TextChoices):
    LEFT = 'LEFT', _('Слева от текста')
    # UP = 'UP', _('Сверху над текстом')
    # DOWN = 'DOWN', _('Снизу под текстом')
    RIGHT = 'RIGHT', _('Справа от текста')


class CourseDescriptionBlock(models.Model):
    course = models.ForeignKey(to=Course,
                               on_delete=models.CASCADE,
                               related_name='description_blocks')
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='course_description_block_images/')
    image_position = models.TextField(choices=CourseDescriptionBlockImagePosition.choices,
                                      default=CourseDescriptionBlockImagePosition.LEFT)
    created = models.DateTimeField(default=now, editable=False)
    order = OrderField(blank=True, for_fields=['course'], default=1)

    class Meta:
        ordering = ('-order',)


class Content(models.Model):
    module = models.ForeignKey(to=Module,
                               on_delete=models.CASCADE,
                               related_name='content_list')
    # related module

    content_type = models.ForeignKey(to=ContentType,
                                     on_delete=models.CASCADE,
                                     limit_choices_to={
                                         'model__in':
                                             (
                                                 'puretext',
                                                 # 'pdf',
                                                 'latex',
                                                 'codelisting',
                                                 'picture',
                                                 'videolink',
                                             )
                                     })
    # Type of content node

    object_id = models.PositiveIntegerField()
    # id of content related object

    item = GenericForeignKey('content_type', 'object_id')
    # assign linked object

    order = OrderField(blank=True, for_fields=['module'], default=1)

    # order number of the content in module

    class Meta:
        ordering = ('order',)


class ItemBase(models.Model):
    owner = models.ForeignKey(to=User,
                              on_delete=models.CASCADE,
                              related_name='%(class)s_related_content')
    # owner of course->module->content block

    title = models.CharField(max_length=150)
    # title of content node

    created = models.DateTimeField(default=now, editable=False)
    # date of object creation

    uploaded = models.DateTimeField(auto_now=True)

    # time of object uploading

    def render(self):
        return render_to_string(
            f'module/content/{self._meta.model_name}.html',
            {'item': self}
        )


class PureText(ItemBase):
    text = models.TextField(blank=True)


# class PDF(ItemBase):
#     file = models.FileField(upload_to='course_pdf_files/')


class LaTeX(ItemBase):
    file = models.FileField(upload_to='course_LaTeX_files/')
    text = models.TextField(blank=True, default='')


class CodeListing(ItemBase):
    code = models.TextField(blank=True)


class Picture(ItemBase):
    image = models.ImageField(upload_to='course_content_images/')


class VideoLink(ItemBase):
    url = models.URLField()


class CourseTask(AbstractTask):
    course = models.ForeignKey(to=Course,
                               related_name='tasks',
                               on_delete=models.DO_NOTHING)

    show_in_task_list = models.BooleanField(default=False)
    solution_file_raw = models.FileField(default=None, upload_to='course_files/')
    solution_file_lang = models.TextField(choices=Language.choices, default=Language.GNU_CXX_14)
    last_validate_solution = models.OneToOneField(to='CourseSolution', blank=True, default=None,
                                                  on_delete=models.DO_NOTHING, null=True)
    difficulty = models.IntegerField(default=1)

    class Meta:
        ordering = ('difficulty',)


class CourseSolution(Solution):
    course = models.ForeignKey(to=Course,
                               related_name='solutions',
                               on_delete=models.DO_NOTHING)
    course_task = models.ForeignKey(to=CourseTask, related_name='course_solutions', on_delete=models.CASCADE,
                                    default=None)

    def get_status(self):
        d = dict()
        for elem in Status.choices:
            d[elem[0]] = elem[1]
        return d[self.status]


class ContestStatus(models.TextChoices):
    WAIT_FOR_START = 'WAIT', _('Ожидается начало контеста.')
    ACTIVE = 'ACTIVE', _('В данный момент контест идет.')
    FINISHED = 'FINISHED', _('Контест завершен. ')


class Contest(models.Model):
    course = models.ForeignKey(to=Course,
                               related_name='contests',
                               on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    start_time = models.DateTimeField(default=datetime.datetime.now(tz=None) + datetime.timedelta(days=1))
    duration = models.DurationField(default=datetime.timedelta(hours=2))
    tasks = models.ManyToManyField(to=CourseTask, related_name='contests', blank=True)
    status = models.TextField(choices=ContestStatus.choices, default=ContestStatus.WAIT_FOR_START)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('-start_time',)


class ContestParticipant(models.Model):
    contest = models.ForeignKey(to=Contest,
                                related_name='participants',
                                on_delete=models.CASCADE,
                                default=None)
    user = models.ForeignKey(to=User, related_name='participated', on_delete=models.CASCADE, default=None)
    penalty = models.IntegerField(default=0)
    deleted = models.BooleanField(default=False)
    delete_reason = models.TextField(default='', blank=True)

    class Meta:
        ordering = ('penalty',)


class ContestSolution(Solution):
    participant = models.ForeignKey(to=ContestParticipant,
                                    related_name='contest_solutions',
                                    on_delete=models.CASCADE,
                                    default=None)

    def get_status(self):
        d = dict()
        for elem in Status.choices:
            d[elem[0]] = elem[1]
        return d[self.status]
